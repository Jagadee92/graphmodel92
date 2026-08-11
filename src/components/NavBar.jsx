import { Link, useNavigate } from "react-router-dom";

export default function NavBar({ profile }) {
  const navigate = useNavigate();

  function logout() {
    localStorage.removeItem("talentgraph_token");
    navigate("/login");
    window.location.reload();
  }

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <Link to="/">
          TalentGraph
        </Link>
      </div>

      <div className="navbar-links">
        {profile ? (
          <>
            <Link to="/">Dashboard</Link>

            <Link to="/jobs">
              Jobs
            </Link>

            <Link to="/recommendations">
              Recommendations
            </Link>

            <Link to="/applications">
              Applications
            </Link>

            <Link to="/profile">
              Profile
            </Link>

            <button
              type="button"
              onClick={logout}
              className="logout-btn"
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <Link to="/login">
              Login
            </Link>

            <Link to="/register">
              Register
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}