import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import api from "../utils/api";
import "./ContactSeller.css";
import { getCookie } from "../utils/cookies";
const ContactSeller = () => {
  const location = useLocation();
  const navigate = useNavigate();
  // Get book from navigation state (passed from Listing or BookDetails)
  const book = location.state?.book;

  const [formData, setFormData] = useState({
    address: "",
    phone: "",
    message: "",
  });
  const [loading, setLoading] = useState(false);

  // Redirect if no book data
  useEffect(() => {
    if (!book) {
      // Optional: Could fetch by ID from URL if we changed route to /contact-seller/:id
      // For now, assume state passing.
    }
  }, [book, navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async () => {
    if (!formData.address && !formData.phone) {
      alert("Please provide at least one contact method (Address or Phone).");
      return;
    }

    if (!formData.message.trim()) {
      alert("Please enter a message.");
      return;
    }

    if (!book || !book.id) {
      alert("Announcement information missing.");
      return;
    }

    try {
      setLoading(true);

      // Map to backend schema ContactSellerRequest
      const payload = {
        announcement_id: Number(book.id),
        title: book.title || "Unknown",
        email: book.user?.email || "buyer@example.com", // Placeholder
        address: formData.address || "",
        phone: formData.phone || "",
        message: formData.message,
      };

      console.log("Sending payload:", payload);

      const response = await api.post("/api/messages/contact-seller", payload, {
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${getCookie("access_token")}`,
        },
      });
      console.log("Response:", response.data);

      const conversationId = response.data.conversation_id;

      alert("Message sent successfully!");
      if (conversationId) {
        navigate(`/message?conversationId=${conversationId}`);
      } else {
        navigate("/message");
      }

    } catch (error) {
      console.error("Contact seller error details:", error.response?.data || error.message);
      const errorDetail = error.response?.data?.detail;
      const errorMessage = Array.isArray(errorDetail)
        ? errorDetail.map(e => `${e.loc.join('.')}: ${e.msg}`).join('\n')
        : (errorDetail || error.response?.data?.message || error.message);

      alert("Error sending message:\n" + errorMessage);
    } finally {
      setLoading(false);
    }
  };


  const handleCancel = () => {
    navigate(-1);
  };

  if (!book) {
    return (
      <div className="contact-seller-wrapper">
        <div className="container mx-auto p-4 text-center">
          <h2>No book selected.</h2>
          <button onClick={() => navigate('/catalog')} className="btn btn-primary">Go to Catalog</button>
        </div>
      </div>
    );
  }

  return (
    <div className="contact-seller-wrapper">
      <div className="contact-seller-card">
        <div className="title-section">
          <h2 className="main-title">Contact the Seller</h2>
          <div className="title-underline"></div>
        </div>

        <div className="form-container">
          <div className="book-cover-section">
            <div className="book-cover-wrapper">
              {book?.image ? (
                <img
                  src={book.image}
                  alt={book.title}
                  className="book-cover-img"
                />
              ) : (
                <div className="book-cover-placeholder">
                  <div className="placeholder-content">
                    <div className="placeholder-icon">✕</div>
                    <div className="placeholder-title">{book.title}</div>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="form-fields">
            <div className="input-group">
              <label className="input-label">Title</label>
              <input
                type="text"
                value={book?.title || "Book Title"}
                disabled
                className="input-field input-readonly"
              />
            </div>

            {/* Show Seller Email if available */}
            <div className="input-group">
              <label className="input-label">Seller Email</label>
              <input
                type="email"
                value={book.user?.email || "N/A"}
                disabled
                className="input-field input-readonly"
              />
            </div>

            <div className="input-group">
              <label className="input-label">
                My Address <span style={{ color: "red" }}>*</span>
              </label>
              <input
                type="text"
                name="address"
                value={formData.address}
                onChange={handleChange}
                className="input-field"
                placeholder="Your address"
                required
              />
            </div>

            <div className="input-group">
              <label className="input-label">
                My Phone <span style={{ color: "red" }}>*</span>
              </label>
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                className="input-field"
                placeholder="05xxxxxxxx"
                required
              />
            </div>

            <div className="input-group">
              <label className="input-label">Message</label>
              <textarea
                name="message"
                value={formData.message}
                onChange={handleChange}
                className="textarea-field"
                placeholder="Describe your request"
              />
            </div>
          </div>

          <div className="button-group">
            <button className="btn btn-cancel" onClick={handleCancel}>
              Cancel
            </button>
            <button className="btn btn-send" onClick={handleSubmit} disabled={loading}>
              {loading ? "Sending..." : "Send"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContactSeller;
