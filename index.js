const map = L.map('map').setView([0, 0], 2);

// add the OpenStreetMap tiles
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  subdomains: ['a', 'b', 'c'],
}).addTo(map);

const marker = L.marker();
marker.bindPopup('Current location');

const drawArc = (lat1, lon1, lat2, lon2) => {
  L.Polyline.Arc([lat1, lon1], [lat2, lon2]).addTo(map);
};

const getElementById = (id) => document.getElementById(id);

const setMarker = (lat, lon) => {
  marker.setLatLng([lat, lon]);
  marker.addTo(map);
};

// drawArc(43.11667, 131.9, 55.75222, 37.61556);
// setMarker(33.11667, 31.9);


let gameStarted = false;
let distanceTravelled = 0;
let batteryLife = 12500;
let goalsAcheived =new Set();

// STATS
const player = getElementById('player');
const battery = getElementById('battery');
const totalDistance = getElementById('totalDistance');
const weatherGoals = getElementById('weatherGoals');

player.innerText = prompt('Enter your name!')|| 'Player 1';
battery.value = batteryLife;
battery.max = batteryLife;
totalDistance.innerText = '0';

// ARIPORTS
const travelForm = getElementById('travelForm');
const origin = getElementById('origin');
const destination = getElementById('destination');

let originAirportData, destinationAirportData;

const setInitialAirport = () => {
  // call the API and get airport details
  originAirportData = {};
  // lat, long
};

const endGame = () => {
  alert('Game Over!!! Start again!!!');
  gameStarted = false;
  originAirportData = null;
  destinationAirportData = null;
  origin.innerText = "";
  destination.innerText = "";
  batteryLife = 12500;
  battery.value = batteryLife;
  distanceTravelled = 0;


   origin.value = '';
  origin.disabled = false;
  destination.value = '';
  totalDistance.innerText = distanceTravelled;
  battery.value = batteryLife;
  goalsAcheived = new Set();
  weatherGoals.innerText = [];
  player.innerText = prompt('Enter your name!')|| 'Player 1';
}


const startJourney = async (e) => {
  e.preventDefault();

  const API = 'http://localhost:5000';
  if (!gameStarted) {
    gameStarted = true;
    const data = await fetch(`${API}/airports/${origin.value}`);
    originAirportData = await data.json();
  }

  const url = `${API}/airports/${destination.value}?prev_lat=${originAirportData.lat}&prev_lon=${originAirportData.lon}`
  const destinationData = await fetch(url);
  destinationAirportData = await destinationData.json();

  console.log(destinationAirportData)

  distanceTravelled += destinationAirportData.distance_travelled;

  const batteryConsumed = destinationAirportData.distance_travelled * 1.5;
  batteryLife = batteryLife - batteryConsumed;
  console.log(batteryConsumed, batteryLife)

  if(batteryLife <= 0){
    endGame();
    return;
  }

  goalsAcheived.add(...destinationAirportData.goals_achieved)

  console.log(originAirportData.lat, originAirportData.lon, destinationAirportData.lat, destinationAirportData.lon)

  if(originAirportData.icao !== destinationAirportData.icao){
    drawArc(originAirportData.lat, originAirportData.lon, destinationAirportData.lat, destinationAirportData.lon);
  }
  setMarker(destinationAirportData.lat, destinationAirportData.lon);


  console.log([...goalsAcheived])

  origin.value = destination.value;
  origin.disabled = true;
  originAirportData = destinationAirportData;
  destination.value = '';
  totalDistance.innerText = distanceTravelled;
  battery.value = batteryLife;
  weatherGoals.innerText = [...goalsAcheived];
};
travelForm.addEventListener('submit', startJourney);

// 60.3172, 24.963301