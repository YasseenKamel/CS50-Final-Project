# YOKO Systems
#### Video Demo:  <URL https://drive.google.com/file/d/1s1TxWiyDVjCFWb28jojzh70CM8LPGTYr/view?usp=sharing>
#### Description:
This is a web app that managed maintenance in a factory/company.

It would run on a local server of a factory which consists of equipment such as production machines.

There are two types of users on the system: a production engineer and a maintenance engineer.

The production engineer will be responsible for identifying what equipment on site may need maintenance and will issue a chosen maintenance engineer to an operation on said equipment.

While each equipment has its default maintenance engineer, the production engineer may freely choose who to issue the "work request" to.

The production engineer issues the work request by indicating the equipment that needs the operation via a code (I have added a few sample equipment codes with their default maintenance engineers in my database just for the sake of demonstrating the system), the priority (from 1 to 5 with 1 being maximum priority) of the operation, the due date, the maintenance engineer it is requested to and the description of the request.

When the production engineer issues the request, the requested maintenance engineer may choose to accept or reject the request (it will be displayed as the request status for the production engineer). When accepting the request, the maintenance engineer will be issued with the task of filling in a "work order" which is a summary for the operation.

The work order can be saved as a draft before submitting.

The work order contains the status of the operation which will either be "ongoing", "onhold" or "completed".

These statuses are updated live to the production engineer who issued the request. The work order contains its description, spare parts used in the operation and the steps taken in the operation.

I have also filled the database with some sample spare part codes with their prices. In the spare parts tab in the work order, the maintenance engineer will add spare parts needed with their quantity by searching for them in either the description column or by code.

The table will increase in rows according to the user's input and rows may be deleted via the "X" button corresponding to the row.
The same procedure goes for the steps tab.

Each step in the table will include its description, duration in hours, number of workers who participated in the step and the hourly wage per worker which will be automated to total work hours and total wages spent on the step.

The user cannot submit the work order as a non-draft order if some fields are missing such as the duration of a certain step.

The user may also edit the work order as needed during the operation as long as it has not been completed.

A work order may also not be completed unless it was set to "ongoing". All work requests will be visible in the homepage of the website (which is opened on logging in by default or by clicking on the "YOKO Systems" title displayed above) and all work orders will be in the "My work orders" tab.

Upon completion of a work order, the user will be issued with a page that displays the planned costs and duration which were inputted in the creation of the work order and will request the user to input the actual duration and costs before submitting which can be later viewed when opening the completed work order in the "actual data" tab. 

Files in this project:
equipment.csv and parts.csv are files that are not used by the project as they only consisted my sample data and I have used reader.py to insert these data in my sql database.
data.db is the database which contains all the websites data.
app.py is the python app for the website which runs the website on "localhost:5500".
The templates folder contains all html pages used in the website with layout.html being the layout that is used by jinja.
The static folder contains the styles and some scripts such as bootstrap and jquery and some images.

Note: In the video I have just sped up a few unnecessary parts to make sure the video first through the duration guidelines.
