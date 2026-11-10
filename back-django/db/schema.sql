BEGIN;
--
-- Create model Station
--
CREATE TABLE "stations" ("id" varchar(20) NOT NULL PRIMARY KEY, "name" varchar(120) NOT NULL, "river" varchar(120) NOT NULL, "municipality" varchar(120) NOT NULL, "active" bool NOT NULL);
--
-- Create model Observation
--
CREATE TABLE "observations" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "metric" varchar(10) NOT NULL, "observed_at" datetime NOT NULL, "value" real NOT NULL, "unit" varchar(10) NOT NULL, "source" varchar(20) NOT NULL, "station_id" varchar(20) NOT NULL REFERENCES "stations" ("id") DEFERRABLE INITIALLY DEFERRED, CONSTRAINT "uniq_observation_station_metric_time" UNIQUE ("station_id", "metric", "observed_at"), CONSTRAINT "check_observation_metric" CHECK ("metric" IN ('level', 'rain')), CONSTRAINT "check_observation_unit" CHECK ("unit" IN ('m', 'mm/h')));
CREATE INDEX "observations_station_id_19cf7841" ON "observations" ("station_id");
CREATE INDEX "idx_obs_station_metric_time" ON "observations" ("station_id", "metric", "observed_at");
COMMIT;
