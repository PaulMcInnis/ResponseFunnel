// This starts the server application and its middleware

// Imports
fs = require("fs");
shell = require("shelljs");
const express = require("express");
const app = express();
const bodyParser = require("body-parser");

// TODO: move these constants into a .env
const dumpFolder = path.join(process.cwd(), "./responses");
const defaultFileExtension = "json";
const DEFAULT_MODE = "writeFile";
const path = require("path");

// Create the folder path in case it doesn't exist
const full_path = path.join(process.cwd(), folderPath);
shell.mkdir("-p", folderPath);

// Change the limits according to your response size
app.use(bodyParser.json({ limit: "50mb", extended: true }));
app.use(bodyParser.urlencoded({ limit: "50mb", extended: true }));

// Be friendly & highly visible
app.get("/", (req, res) =>
  res.send(
    `Hello, send HTML responses to my /write endpoint to save them locally in the folder: '${dumpFolder}.`
  )
);

// Endpoint responsible for actually saving data
app.post("/write", (req, res) => {
  const extension = req.body.fileExtension || defaultFileExtension;
  const fsMode = req.body.mode || DEFAULT_MODE;
  const uniqueIdentifier = req.body.uniqueIdentifier
    ? typeof req.body.uniqueIdentifier === "boolean"
      ? Date.now()
      : req.body.uniqueIdentifier
    : false;
  const filename = `${req.body.requestName}${uniqueIdentifier || ""}`;
  const filePath = `${path.join(folderPath, filename)}.${extension}`;
  const options = req.body.options || undefined;

  fs[fsMode](filePath, req.body.responseData, options, (err) => {
    if (err) {
      console.log(err);
      res.send("Error");
    } else {
      res.send("Success");
    }
  });
});

// Start the server and write some logs to let the user know
app.listen(3000, () => {
  console.log("ResponsesToFile App Started.");
  console.log(
    `Data is being stored at location: ${path.join(process.cwd(), folderPath)}`
  );
});
