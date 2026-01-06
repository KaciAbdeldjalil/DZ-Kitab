import { useState } from "react";
import "./UsersAdmin.css";
import NavAdmin from "./navbarAdmin";
const initialUsers = [
  { id: 1, name: "Ahmed Benali", email: "ahmed@gmail.com", role: "User", status: "active" },
  { id: 2, name: "Sara Kacem", email: "sara@gmail.com", role: "Admin", status: "active" },
  { id: 3, name: "Yanis Omar", email: "yanis@gmail.com", role: "User", status: "blocked" },
];


export default function AdminUsers() {
  const [users, setUsers] = useState(initialUsers);
  const [search, setSearch] = useState("");

  const toggleStatus = (id) => {
    setUsers(users.map(u =>
      u.id === id ? { ...u, status: u.status === "active" ? "blocked" : "active" } : u
    ));
  };

  const deleteUser = (id) => {
    if (window.confirm("Are you sure you want to delete this user?")) {
      setUsers(users.filter(u => u.id !== id));
    }
  };

  const filteredUsers = users.filter(user =>
    user.name.toLowerCase().includes(search.toLowerCase()) ||
    user.email.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <>
      <NavAdmin />
      <div className="admin-page">
        <h1 className="admin-title">User Management</h1>

        <div className="admin-search">
          <input
            type="text"
            placeholder="Search by name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="admin-card">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredUsers.length > 0 ? (
                filteredUsers.map(user => (
                  <tr key={user.id}>
                    <td>{user.name}</td>
                    <td>{user.email}</td>
                    <td><span className={`role ${user.role.toLowerCase()}`}>{user.role}</span></td>
                    <td><span className={`status ${user.status}`}>{user.status === "active" ? "Active" : "Blocked"}</span></td>
                    <td className="actions">
                      <button className="btn btn-toggle" onClick={() => toggleStatus(user.id)}>
                        {user.status === "active" ? "Block" : "Activate"}
                      </button>
                      <button className="btn btn-delete" onClick={() => deleteUser(user.id)}>Delete</button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr><td colSpan="5" className="no-data">No users found</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
