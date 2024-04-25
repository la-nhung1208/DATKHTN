const express = require("express");
const mongoose = require("mongoose");
const app = express();
const ejs = require("ejs");
const mqtt = require("mqtt");

const uri = "mongodb+srv://nhung:Nhung2002@nhung.wbglqvx.mongodb.net/doannhung";

const dataSchema = new mongoose.Schema({
  temperature: Number,
  humidity: Number,
  soil_moisture: Number,
  lux: Number,
});

const Data = mongoose.model("Data", dataSchema, "dulieudoannhung");

mongoose
  .connect(uri, {
    useNewUrlParser: true,
    useUnifiedTopology: true,
  })
  .then(() => {
    console.log("Connected to MongoDB");
  })
  .catch((err) => {
    console.error("Error connecting to MongoDB:", err.message);
  });

const options = {
  username: "lanhung",
  password: "Lanhung2002",
  rejectUnauthorized: false,
};

const client = mqtt.connect(
  "tls://79965c95be5248e8a61185e66bf3c38f.s1.eu.hivemq.cloud:8883",
  options
);

client.on("connect", function () {
  console.log("Connected to MQTT");
  client.subscribe("dulieumqtt");
});

client.on("message", function (topic, message) {
  const data = JSON.parse(message);
  var giatrinhietdo = data.temperature.toFixed(2);
  var giatridoam = data.humidity;
  var giatridoamdat = data.soil_moisture;
  var giatricuongdoanhsang = data.lux.toFixed(2);

  const newData = new Data({
    temperature: giatrinhietdo,
    humidity: giatridoam,
    soil_moisture: giatridoamdat,
    lux: giatricuongdoanhsang,
  });
  newData
    .save()
    .then(() => {
      console.log("Data saved to MongoDB");
    })
    .catch((err) => {
      console.error("Error saving data to MongoDB:", err.message);
    });

  io.emit("capnhatnhietdo", giatrinhietdo);
  io.emit("capnhatdoam", giatridoam);
  io.emit("capnhatdoamdat", giatridoamdat);
  io.emit("capnhatcuongdoanhsang", giatricuongdoanhsang);
});

const server = require("http").Server(app);
const io = require("socket.io")(server);
const port = 1208;
server.listen(port);

app.set("view engine", "ejs");
app.set("views", "/home/nhung/DATKHTN/NhungWebserver/views/");
app.use(
  "/public",
  express.static("/home/nhung/DATKHTN/NhungWebserver/public/")
);
app.get("/", function (req, res) {
  res.render("index");
});

io.on("connection", function (socket) {
  socket.on("relayio1", function (relayValue) {
    const mqttMessage = relayValue === 1 ? "0" : "1";
    client.publish("relay1", mqttMessage);
  });
  socket.on("relayio2", function (relayValue) {
    const mqttMessage = relayValue === 1 ? "0" : "1";
    client.publish("relay2", mqttMessage);
  });
});
