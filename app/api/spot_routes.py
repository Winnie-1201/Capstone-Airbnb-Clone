from flask import Blueprint, request
from flask_login import login_required, current_user
from app.models import db, Spot, Review, Booking, Experience, Wishlist, Image
from app.forms import SpotForm, ReviewForm, BookingForm, ExperienceForm, WishlistForm, ImageForm

spot_routes = Blueprint('spots', __name__)

@spot_routes.route('')
def all_spots():
    '''
    Query for all spots and return them in a list of dictionaries
    '''
    params = request.args # [('name', 'Beach')]
    if len(params) == 0:
        spots = Spot.query.all()
        # print('all spots', spots)
        # print('one spot', spots[0].to_dict_basic())
        return {"spots": [spot.to_dict_basic() for spot in spots]}
    else:
        # test if it works
        spots = Spot.query.all()
        if params.get('name'):
            spots = spots.filter_by(name=params.get('name'))
        if params.get('min'):
            spots = spots.filter(Spot.price >= params.get('min'))
        if params.get('max'):
            spots = spots.filter(Spot.price <= params.get('max'))
        spots = spots.all()

        return {'spots': [spot.to_dict() for spot in spots]}


@spot_routes.route('/current')
@login_required
def user_spots():
    '''
    Query for all spots of current user and return them in a list of dictionaries
    '''
    spots = Spot.query.filter_by(userId=current_user.id).all()

    return {"spots": [spot.to_dict() for spot in spots]}


@spot_routes.route("/<int:id>")
def spot_by_id(id):
    '''
    Query one spot by its id and return it in a disctionary
    '''
    spot = Spot.query.get(id)

    print("-------")
    print("spot", spot)
    return {'spot': spot.to_dict_details()}


@spot_routes.route("", methods=["POST"])
@login_required
def create_spot():

    form = SpotForm()
    form['csrf_token'].data = request.cookies['csrf_token']

    if form.validate_on_submit:
        address = form.data["address"]
        city = form.data["city"]
        state = form.data["state"]
        country = form.data["country"]
        name = form.data["name"]
        price = form.data["price"]
        tags = form.data["tags"]
        guests = form.data["guests"]
        bedroom = form.data["bedroom"]
        beds = form.data["beds"]
        bath = form.data["bath"]
        preview_img = form.data["preview_img"]

        new_spot = Spot(
            address=address,
            city=city,
            state=state,
            country=country,
            name=name,
            price=price,
            tags=tags,
            guests=guests,
            bedroom=bedroom,
            beds=beds,
            bath=bath,
            preview_img=preview_img,
            userId=current_user.id,
        )

        db.session.add(new_spot)
        db.session.commit()

        return new_spot.to_dict()

    if form.errors:
        return form.errors

    
@spot_routes.route('<int:id>', methods=["PUT"])
@login_required
def edit_spot(id):
    form = SpotForm()
    form['csrf_token'].data = request.cookies['csrf_token']
 
    spot = Spot.query.get(id)
    if spot.userId == current_user.id:
        if form.validate_on_submit:
            if form.data["address"]: spot.address = form.data["address"] 
            if form.data["city"]: spot.city = form.data["city"] 
            if form.data["state"]: spot.state = form.data["state"] 
            if form.data["country"]: spot.country = form.data["country"] 
            if form.data["name"]: spot.name = form.data["name"] 
            if form.data["price"]: spot.price = form.data["price"]
            if form.data["tags"]: spot.tags = form.data["tags"]


            db.session.commit()

            return spot.to_dict()
        
        if form.errors:
            return form.errors
    else:
        return {'error': 'You do not have the access.'}


@spot_routes.route('<int:id>', methods=["DELETE"])
@login_required
def delete_spot(id):
    spot = Spot.query.get(id)

    if spot.userId == current_user.id:
        db.session.delete(spot)
        db.session.commit()

        return {'message': 'The spot has been deleted!'}

    else:
        return {'error': 'You do not have the access.'}


@spot_routes.route('/<int:spotId>/reviews')
def spot_reviews(spotId):

    '''
    Query for all reviews of a spot and return them in a list of dictionaries
    '''
    reviews = Review.query.filter_by(spotId=spotId).all()

    return {'Reviews': [review.to_dict() for review in reviews]}
        

@spot_routes.route('<int:spotId>/reviews', methods=["POST"])
@login_required
def add_review(spotId):

    '''
    Query for creating a review based on the spotId and return it as a dictionary
    '''

    form = ReviewForm()
    form['csrf_token'].data = request.cookies['csrf_token']

    review = Review.query.filter_by(userId=current_user.id, spotId=spotId).first()

    if review:
        return {'error': 'You have posted a review already.'}

    if form.validate_on_submit:
        content = form.data["content"]
        cleanliness = form.data["cleanliness"]
        check_in = form.data["check_in"]
        communicatoin =form.data["communicatoin"]
        value = form.data["value"]
        location = form.data["location"]
        accuracy = form.data["accuracy"]

        new_review = Review(
            content, 
            cleanliness,
            check_in,
            communicatoin,
            value,
            location,
            accuracy,
            userId=current_user.id,
            spotId=spotId
        )

        db.session.add(new_review)
        db.session.commit()

        return new_review.to_dict()
    
    if form.errors:
        return form.errors


@spot_routes.route('/<int:spotId>/bookings')
@login_required
def spot_bookings(spotId):
    '''
    Query for a specific spot's bookings and return them in a list of dictionaries
    '''

    bookings = Booking.query.filter_by(spotId=spotId).all()

    return {'Bookings': [booking.to_dict() for booking in bookings]}

        

@spot_routes.route('/<int:spotId>/bookings', methods=['POST'])
@login_required
def create_booking(spotId):
    '''
    Query for creating a booking for a spot by the spotId and return 
    it in a dictionary
    '''

    form = BookingForm()
    form['csrf_token'].data = request.cookies['csrf_token']

    if form.validate_on_submit:
        start = form.data['start']
        end = form.data['end']

        new_booking = Booking(start, end, spotId=spotId, userId=current_user.id)

        db.session.add(new_booking)
        db.session.commit()

        return new_booking.to_dict()


@spot_routes.route('/<int:spotId>/experiences')
def spot_experiences(spotId):
    '''
    Query for getting a spot's experiences based on its id and 
    return them in a list of dictionaries
    '''
    experiences = Experience.query.filter_by(spotId=spotId)

    return {'Experiences': [e.to_dict() for e in experiences]}


@spot_routes.route('/<int:spotId>/experiences', methods=['POST'])
@login_required
def create_experience(spotId):
    '''
    Query for create an experience a spot based on its id and
    return it as a dictionary
    '''
    form = ExperienceForm()
    form['csrf_token'].data = request.cookies['csrf_token']

    if form.validate_on_submit:
        duration = form.data['duration']
        tags = form.data['tags']
        content = form.data['content']
        name = form.data['name']

        new_exp = Experience(duration, tags, content, name, userId=current_user.id, spotId=spotId)
        
        db.session.add(new_exp)
        db.session.commit()

        return new_exp.to_dict()
    
    if form.errors:
        return form.errors


@spot_routes.route('/<int:spotId>/wishlists/<int:wishlistId>', methods=['POST'])
@login_required
def add_spot_to_wishlist(spotId, wishlistId):

    wishlist = Wishlist.query.get(wishlistId)

    if wishlist:

        form = WishlistForm()
        form['csrf_token'].data = request.cookies['csrf_token']

        if form.validate_on_submit:
            wishlist.spots.append(spotId)

            db.session.commt()

            return wishlist.to_dict()

        if form.errors:
            return form.errors

    else:
        return {'error': 'The wishlist is not found.'} 



@spot_routes.route('/<int:spotId>/images', methods=['POST'])
@login_required
def add_imgage(spotId):

    spot = Spot.query.get(spotId)

    if spot:
        if spot.userId == current_user.id:

            form = ImageForm()
            form['csrf_token'].data = request.cookies['csrf_token']

            if form.validate_on_submit:
                # not sure yet
                pass


