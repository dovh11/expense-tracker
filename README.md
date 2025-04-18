# Expense Tracker
### Instruction: 
Execute `flask run` on your VSCode Terminal to run this web app locally.
```
flask run
```
### Description:
- This web app helps people tracking all expenses manually on their own account.
- I have implemented this web app almost from scratch and just by myself.
- This is my first Computer Science project.

## Technologies Used
- Languages: Python, SQL, HTML, CSS.
- Frameworks: Bootstrap, Flask.
- Database: SQLite.

## Main Features
### Login
- Log user in.
### Logout
- Log user out.
### Register
- Register a new account with user's email.
### Homepage *(default folder)*
- Users have an opportunity to tracking their expenses inserted in this web app, by querying the explicit year, month or day, depending on their demand.
- After querying, a table will be showed with all informations of items inserted. There are extra details include *Total Price* and *Available Cash* will be given to users.
### Insert
- To insert an item, user have to complete the form with 3 fields:
    - *Description*: describe about the item they have afforded.
    - *Category*: a list of options, simply ask for which type of item is.
    - *Price*: The price of item, calculated in dollars.
### Delete
- To delete an item, user have to submit into to a form the explicit time (year, month, date, hour, minute, second) when item was being inserted. This details about time can be retrived in Homepage.
- In server side, I have implemented some lines code so that when deleting an item, server have to detect both the informations about time inserting item and the cookies of user. 
### History
- Show all items the user has added to this web app (excluding deleted items) from the time the account was created up until now.
### Top-up
- Help a person top up money into their account, so they can balance their budget dynamically.
### Withdraw
- Help a person withdraw money from their account, so they can balance their budget dynamically.
### Feedback
- Everyone with an account can leave their feedback with comments and stars in Expense Tracker, then I direct users to a page with all feedbacks from others. This action will help me improve my web app to be more convenient and user-friendly.

## Note
> If you guys interested in my Expense Tracker web app, feel free to clone and explore it on your own device. However, since I have submitted this web app project to an online course, you are not allowed to use it for submitting as your own project in online courses, lest both you and I will be got trouble.