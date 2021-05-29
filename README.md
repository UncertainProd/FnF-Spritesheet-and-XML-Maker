# FnF-Spritesheet-and-XML-Maker
A Friday Night Funkin' mod making helper tool that allows you to generate XML files and spritesheets from induvidual pngs. This is a free and open-source mini-replacement tool to the "Generate Spritesheet" functionality in Adobe Animate/Flash

## How to use this tool:
<img src="./docs/InitScreen.png" />
The name of your character goes into the textbox at the top. This is necessary as the final xml and png files will be named accordingly.
Eg: If you name you character <b>Pixel-GF</b> the files generated will be named <b>Pixel-GF.png</b> and <b>Pixel-GF.xml</b>
<strong>Do not leave this box blank as it will crash the application!</strong>

### Adding sprite frames
Click the button named "Add Frame Image" to add each pose as frame in the spritesheet, as shown below:
<img src="./docs/added-sprites.png" />

Each "frame" of your spritesheet has 2 buttons on either side:
<img src="./docs/frame-buttons.png" />
Use the "Pose Names" button to name each pose (Eg: 'gfPixel sing down' or 'gfPixel idle') and to delete any individual frame click the "Delete Frame" button.

### Clip to bounding box
If your induvidual frames have extra whitespace in them and you want them all cropped to just their bounding box, click this checkbox before generating the files.
<img src="./docs/bbox-comparison.png" width="100px" />
On left is how the image will be considered if this checkbox is left unchecked. On the right is how it'll be considered if it is checked. <small>(Side note: Most of the time you won't really have to use this feature, but it is provided just in case)</small>

### Generating the final XML and PNG files
When you're done adding all the frames and giving them pose names, it's time to generate the final PNG and XML files!
To do so, just click the "Generate XML" button. Select the location you want the files saved and the xml and png files will be generated.
<img src="./docs/final-files.png" width="500px" />


<small>Note: Although the main functionality of this application is complete, there are still minor crashing issues and bugs that may need fixing. Updates will be on the way soon. Stay tuned!</small>

## Running from source:
In order to run this from source, you will need <a href="https://www.python.org/downloads/release/python-390/">python v3.9</a> (minimum) and pip installed on your device (pip should come pre-installed with python). Install the dependencies first by opening the command line, navigating to this directory and typing ``` pip install -r requirements.txt ```. Once that is done type ``` python xmlpngUI.py ``` to run the application (Sometimes you need to type ``` python3 ``` instead of just ``` python ```).