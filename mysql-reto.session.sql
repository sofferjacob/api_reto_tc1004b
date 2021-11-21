-- Command to spin up docker container:
-- docker run --name reto-iot -p 3306:3306 -p 33060:33060 -e MYSQL_ROOT_PASSWORD=reto -d mysql:latest
CREATE DATABASE reto;
USE reto;
-- @block
CREATE TABLE location(
    locationId INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    capacity INT NOT NULL,
    size INT NOT NULL
);
CREATE TABLE model(
    modelId INT PRIMARY KEY AUTO_INCREMENT,
    modelName VARCHAR(255) NOT NULL UNIQUE
);
CREATE TABLE device(
    deviceId INT AUTO_INCREMENT,
    status TINYINT UNSIGNED NOT NULL,
    mac VARCHAR(17) UNIQUE NOT NULL,
    locationId INT NOT NULL,
    modelId INT NOT NULL,
    PRIMARY KEY (deviceId),
    FOREIGN KEY (locationId) REFERENCES location(locationId),
    FOREIGN KEY (modelId) REFERENCES model(modelId)
);
CREATE TABLE parameter(
    parameterId INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    unit VARCHAR(15) NOT NULL,
    min DOUBLE NOT NULL,
    max DOUBLE NOT NULL
);
CREATE TABLE model_parameters(
    id INT AUTO_INCREMENT,
    modelId INT NOT NULL,
    parameterId INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY (modelId) REFERENCES model(modelId),
    FOREIGN KEY (parameterId) REFERENCES parameter(parameterId)
);
CREATE TABLE measurement(
    measurementId INT AUTO_INCREMENT,
    value double NOT NULL,
    timestamp DATETIME NOT NULL,
    parameterId INT NOT NULL,
    deviceId INT NOT NULL,
    PRIMARY KEY (measurementId),
    FOREIGN KEY (parameterId) REFERENCES parameter(parameterId),
    FOREIGN KEY (deviceId) REFERENCES device(deviceId)
);