Проект Booking

Features:
- Apartment management: create, view, update, and delete.
- Reservation management: create, view, update, and delete.
- User management: register, authenticate, and view profile.
- Reservation rating: add reviews and ratings.

Endpoints:
- /apartments/ [GET, POST]: Get a list of apartments, create a new apartment.
- /apartments/{id}/ [GET, PUT, DELETE]: Get, update, and delete a specific apartment.
- /reservations/ [GET, POST]: Get a list of reservations, create a new reservation.
- /reservations/{id}/ [GET, PUT, DELETE]: Get, update, and delete a specific reservation, add a review upon completion of the reservation.
- /apartments/{id}/ratings/ [GET]: View reviews for apartments.
- /users/register/ [POST]: Register a new user.
- /users/login/ [POST]: User authentication.
- /users/profile/ [GET]: Get the current user's profile.
- /ratings/ [GET, POST]: Get a list of reviews, add a new review.
- /ratings/{id}/ [GET, PUT, DELETE]: Get, update, delete a specific review.
