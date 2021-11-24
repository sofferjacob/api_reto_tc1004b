-- Command to spin up docker container:
-- docker run --name reto-iot -p 3306:3306 -p 33060:33060 -e MYSQL_ROOT_PASSWORD=reto -d mysql:latest
-- @block
CREATE TABLE location(
    "locationId" SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    capacity INT NOT NULL,
    size INT NOT NULL
);
CREATE TABLE model(
    "modelId" SERIAL PRIMARY KEY,
    "modelName" VARCHAR(255) NOT NULL UNIQUE
);
CREATE TABLE device(
    "deviceId" SERIAL,
    status SMALLINT NOT NULL,
    mac VARCHAR(30) UNIQUE NOT NULL,
    "locationId" INT NOT NULL,
    "modelId" INT NOT NULL,
    PRIMARY KEY ("deviceId"),
    FOREIGN KEY ("locationId") REFERENCES location("locationId"),
    FOREIGN KEY ("modelId") REFERENCES model("modelId")
);
CREATE TABLE parameter(
    "parameterId" SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    unit VARCHAR(15) NOT NULL,
    min DOUBLE PRECISION NOT NULL,
    max DOUBLE PRECISION NOT NULL
);
CREATE TABLE model_parameters(
    id SERIAL,
    "modelId" INT NOT NULL,
    "parameterId" INT NOT NULL,
    PRIMARY KEY (id),
    FOREIGN KEY ("modelId") REFERENCES model("modelId"),
    FOREIGN KEY ("parameterId") REFERENCES parameter("parameterId")
);
CREATE TABLE measurement(
    "measurementId" SERIAL,
    value DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    "parameterId" INT NOT NULL,
    "deviceId" INT NOT NULL,
    PRIMARY KEY ("measurementId"),
    FOREIGN KEY ("parameterId") REFERENCES parameter("parameterId"),
    FOREIGN KEY ("deviceId") REFERENCES device("deviceId")
);