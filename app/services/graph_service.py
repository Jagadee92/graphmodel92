from datetime import datetime, timezone
import uuid
from app.db.session import get_session

def _record_dict(record):
    return record.data()

def candidate_by_email(email: str):
    query = '''
    MATCH (c:Candidate {email: $email})
    RETURN c
    '''
    with get_session() as session:
        record = session.run(query, email=email).single()
        return record["c"] if record else None

def candidate_by_id(candidate_id: str):
    query = '''
    MATCH (c:Candidate {id: $candidate_id})
    RETURN c
    '''
    with get_session() as session:
        record = session.run(query, candidate_id=candidate_id).single()
        return record["c"] if record else None

def create_candidate(data: dict, password_hash: str):
    candidate_id = "C-" + uuid.uuid4().hex[:8].upper()
    query = '''
    CREATE (c:Candidate {
        id: $id,
        name: $name,
        email: $email,
        password_hash: $password_hash,
        location: $location,
        bio: $bio,
        created_at: datetime()
    })
    WITH c
    UNWIND $skills AS skill_name
    MERGE (s:Skill {name: skill_name})
    MERGE (c)-[:HAS_SKILL]->(s)
    RETURN c
    '''
    params = {
        "id": candidate_id,
        "name": data["name"],
        "email": data["email"].lower(),
        "password_hash": password_hash,
        "location": data["location"],
        "bio": data.get("bio", ""),
        "skills": list(dict.fromkeys(data.get("skills", []))),
    }
    with get_session() as session:
        return session.run(query, **params).single()["c"]

def profile(candidate_id: str):
    query = '''
    MATCH (c:Candidate {id: $candidate_id})
    OPTIONAL MATCH (c)-[:HAS_SKILL]->(s:Skill)
    OPTIONAL MATCH (c)-[:WORKED_ON]->(p:Project)
    OPTIONAL MATCH (p)-[:USES_TECH]->(ps:Skill)
    OPTIONAL MATCH (c)-[a:APPLIED_TO]->(j:Job)-[:POSTED_BY]->(co:Company)
    RETURN c,
           collect(DISTINCT s.name) AS skills,
           collect(DISTINCT {id:p.id, name:p.name, description:p.description}) AS projects,
           collect(DISTINCT {
              id:a.id, job_id:j.id, job_title:j.title, company:co.name,
              status:a.status, submitted_at:toString(a.submitted_at),
              email_notification:a.email_notification
           }) AS applications
    '''
    with get_session() as session:
        record = session.run(query, candidate_id=candidate_id).single()
        if not record:
            return None
        c = dict(record["c"])
        c.pop("password_hash", None)
        return {
            "candidate": c,
            "skills": [x for x in record["skills"] if x],
            "projects": [x for x in record["projects"] if x.get("id")],
            "applications": [x for x in record["applications"] if x.get("id")],
        }

def update_profile(candidate_id: str, data: dict):
    query = '''
    MATCH (c:Candidate {id: $candidate_id})
    SET c.name = $name, c.location = $location, c.bio = $bio
    WITH c
    OPTIONAL MATCH (c)-[old:HAS_SKILL]->(:Skill)
    DELETE old
    WITH c
    UNWIND $skills AS skill_name
    MERGE (s:Skill {name: skill_name})
    MERGE (c)-[:HAS_SKILL]->(s)
    RETURN c
    '''
    with get_session() as session:
        record = session.run(
            query,
            candidate_id=candidate_id,
            name=data["name"],
            location=data["location"],
            bio=data.get("bio", ""),
            skills=list(dict.fromkeys(data.get("skills", []))),
        ).single()
        return dict(record["c"])

def list_jobs(search: str | None = None, skill: str | None = None):
    query = '''
    MATCH (j:Job)-[:POSTED_BY]->(co:Company)
    OPTIONAL MATCH (j)-[:REQUIRES_SKILL]->(s:Skill)
    WHERE ($search IS NULL OR toLower(j.title) CONTAINS toLower($search))
      AND ($skill IS NULL OR toLower(s.name) = toLower($skill))
    RETURN j.id AS id, j.title AS title, j.location AS location,
           j.description AS description, j.salary_range AS salary_range,
           co.name AS company, collect(DISTINCT s.name) AS skills
    ORDER BY j.title
    '''
    with get_session() as session:
        return [_record_dict(r) for r in session.run(query, search=search, skill=skill)]

def job_by_id(job_id: str):
    query = '''
    MATCH (j:Job {id: $job_id})-[:POSTED_BY]->(co:Company)
    OPTIONAL MATCH (j)-[:REQUIRES_SKILL]->(s:Skill)
    RETURN j.id AS id, j.title AS title, j.location AS location,
           j.description AS description, j.salary_range AS salary_range,
           co.name AS company, collect(DISTINCT s.name) AS skills
    '''
    with get_session() as session:
        r = session.run(query, job_id=job_id).single()
        return _record_dict(r) if r else None

def recommendations(candidate_id: str):
    query = '''
    MATCH (c:Candidate {id: $candidate_id})-[:HAS_SKILL]->(s:Skill)
          <-[:REQUIRES_SKILL]-(j:Job)-[:POSTED_BY]->(co:Company)
    WITH j, co, collect(DISTINCT s.name) AS matched_skills,
         count(DISTINCT s) AS matched
    OPTIONAL MATCH (j)-[:REQUIRES_SKILL]->(required:Skill)
    WITH j, co, matched_skills, matched, count(DISTINCT required) AS required_count
    RETURN j.id AS id, j.title AS title, co.name AS company,
           j.location AS location, matched_skills,
           CASE WHEN required_count = 0 THEN 0
                ELSE toInteger(100.0 * matched / required_count)
           END AS match_score
    ORDER BY match_score DESC, title
    LIMIT 20
    '''
    with get_session() as session:
        return [_record_dict(r) for r in session.run(query, candidate_id=candidate_id)]

def has_applied(candidate_id: str, job_id: str):
    query = '''
    MATCH (c:Candidate {id:$candidate_id})-[a:APPLIED_TO]->(j:Job {id:$job_id})
    RETURN a
    '''
    with get_session() as session:
        return session.run(query, candidate_id=candidate_id, job_id=job_id).single() is not None

def create_attempt(candidate_id: str, job_id: str, status: str, reason: str = "", email_notification: str = ""):
    attempt_id = "ATT-" + uuid.uuid4().hex[:10].upper()
    query = '''
    MATCH (c:Candidate {id:$candidate_id}), (j:Job {id:$job_id})
    CREATE (a:ApplicationAttempt {
        id:$attempt_id,
        status:$status,
        reason:$reason,
        email_notification:$email_notification,
        created_at:datetime()
    })
    CREATE (c)-[:MADE_ATTEMPT]->(a)
    CREATE (a)-[:FOR_JOB]->(j)
    RETURN a
    '''
    with get_session() as session:
        return dict(session.run(
            query,
            candidate_id=candidate_id,
            job_id=job_id,
            attempt_id=attempt_id,
            status=status,
            reason=reason,
            email_notification=email_notification,
        ).single()["a"])

def create_application(candidate_id: str, job_id: str, cover_note: str, email_notification: str):
    application_id = "APP-" + uuid.uuid4().hex[:10].upper()
    query = '''
    MATCH (c:Candidate {id:$candidate_id}), (j:Job {id:$job_id})
    CREATE (c)-[a:APPLIED_TO {
        id:$application_id,
        status:"SUBMITTED",
        cover_note:$cover_note,
        submitted_at:datetime(),
        email_notification:$email_notification
    }]->(j)
    RETURN a
    '''
    with get_session() as session:
        return dict(session.run(
            query,
            candidate_id=candidate_id,
            job_id=job_id,
            application_id=application_id,
            cover_note=cover_note,
            email_notification=email_notification,
        ).single()["a"])

def stats():
    query = '''
    OPTIONAL MATCH (c:Candidate) WITH count(c) AS candidates
    OPTIONAL MATCH (j:Job) WITH candidates, count(j) AS jobs
    OPTIONAL MATCH (co:Company) WITH candidates, jobs, count(co) AS companies
    OPTIONAL MATCH (s:Skill) WITH candidates, jobs, companies, count(s) AS skills
    OPTIONAL MATCH ()-[r]->() RETURN candidates, jobs, companies, skills, count(r) AS relationships
    '''
    with get_session() as session:
        return _record_dict(session.run(query).single())

def skill_network(skill_name: str):
    query = '''
    MATCH (s:Skill {name:$skill_name})
    OPTIONAL MATCH (c:Candidate)-[:HAS_SKILL]->(s)
    OPTIONAL MATCH (j:Job)-[:REQUIRES_SKILL]->(s)
    OPTIONAL MATCH (j)-[:POSTED_BY]->(co:Company)
    RETURN s.name AS skill,
           collect(DISTINCT c.name) AS candidates,
           collect(DISTINCT {title:j.title, company:co.name}) AS jobs
    '''
    with get_session() as session:
        r = session.run(query, skill_name=skill_name).single()
        return _record_dict(r) if r else None
