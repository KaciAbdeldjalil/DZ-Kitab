import React, { createContext, useState, useEffect, useContext } from "react";

const WishlistContext = createContext();

export const useWishlist = () => useContext(WishlistContext);

export const WishlistProvider = ({ children }) => {
  const [wishlist, setWishlist] = useState(() => {
    const saved = localStorage.getItem("wishlist");
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    localStorage.setItem("wishlist", JSON.stringify(wishlist));
  }, [wishlist]);

  const addToWishlist = (bookId) => {
    setWishlist((prev) => {
      if (!prev.includes(bookId)) {
        return [...prev, bookId];
      }
      return prev;
    });
  };

  const removeFromWishlist = (bookId) => {
    setWishlist((prev) => prev.filter((id) => id !== bookId));
  };

  const isInWishlist = (bookId) => {
    return wishlist.includes(bookId);
  };

  const toggleWishlist = (bookId) => {
    if (isInWishlist(bookId)) {
      removeFromWishlist(bookId);
    } else {
      addToWishlist(bookId);
    }
  };

  return (
    <WishlistContext.Provider
      value={{
        wishlist,
        addToWishlist,
        removeFromWishlist,
        isInWishlist,
        toggleWishlist,
      }}
    >
      {children}
    </WishlistContext.Provider>
  );
};
