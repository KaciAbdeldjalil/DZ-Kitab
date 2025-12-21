import React from "react";
import { useWishlist } from "../context/WishlistContext";
import { booksData } from "../data/booksData";
import "./Wishlist.css";

const Wishlist = () => {
  const { wishlist, removeFromWishlist } = useWishlist();

  const wishlistItems = wishlist
    .map((id) => booksData.find((book) => book.id === id))
    .filter(Boolean);

  return (
    <div className="wishlist-container">
      <div className="wishlist-top-section">
        <div className="wishlist-heart-icon">
          <svg
            width="50"
            height="50"
            viewBox="0 0 24 24"
            fill="none"
            stroke="#000000"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path>
          </svg>
        </div>
        <h1 className="wishlist-title">My Wishlist</h1>
      </div>

      <div className="wishlist-table">
        <div className="wishlist-header-row">
          <div className="wishlist-col-spacer-left"></div>
          <div className="wishlist-col-header-name">Book Name</div>
          <div className="wishlist-col-header-price">Price</div>
          <div className="wishlist-col-header-status">Status</div>
          <div className="wishlist-col-spacer-right"></div>
        </div>

        {wishlistItems.length === 0 ? (
          <div
            style={{ textAlign: "center", padding: "40px", fontSize: "18px" }}
          >
            Your wishlist is empty.
          </div>
        ) : (
          wishlistItems.map((item) => (
            <div key={item.id} className="wishlist-row">
              <div
                className="wishlist-col-delete"
                onClick={() => removeFromWishlist(item.id)}
              >
                <svg
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="#000000"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </div>
              <div className="wishlist-col-image">
                <img
                  src={item.image}
                  alt={item.title}
                  className="wishlist-book-img"
                />
              </div>
              <div className="wishlist-col-name">{item.title}</div>
              <div className="wishlist-col-price">{item.price} DA</div>
              <div
                className={`wishlist-col-status ${
                  item.status === "Available"
                    ? "status-available"
                    : "status-unavailable"
                }`}
              >
                {item.status}
              </div>
              <div className="wishlist-col-action">
                {item.status === "Available" && (
                  <button className="wishlist-buy-btn">Buy Now</button>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Wishlist;
