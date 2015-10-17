/**
 * schema.sql
 * Copyright 2015 Bengfort.com
 * Version: Flashcube v2
 *
 * Author:  Benjamin Bengfort <benjamin@bengfort.com>
 * Author:  Allen Leis <allen.leis@gmail.com>
 * Author:  Jenny Kim <spaztick@gmail.com>
 *
 * Created: Fri Oct 16 20:53:09 2015 -0400
 *
 * CREATE statements for tables and indicies of the Flashcube Schema v2
 */

-------------------------------------------------------------------------
-- Ensure transaction security by placing all CREATE and ALTER statements
-- inside of `BEGIN` and `COMMIT` statements.
-------------------------------------------------------------------------

BEGIN;

/**
 *  CREATE ENTITY TABLES
 */

-------------------------------------------------------------------------
-- Client Table
-------------------------------------------------------------------------

-- DROP TABLE IF EXISTS "client";

CREATE TABLE IF NOT EXISTS "client"
(
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(255) NOT NULL UNIQUE,
    "description" VARCHAR(1024),
    "ipaddr" INET,
    "apikey" CHAR(22) NOT NULL UNIQUE,
    "secret" CHAR(43) NOT NULL UNIQUE,
    "created" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-------------------------------------------------------------------------
-- Member Table
-------------------------------------------------------------------------

-- DROP TABLE IF EXISTS "credential";

CREATE TABLE IF NOT EXISTS "credential"
(
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "email_hash" CHAR(44) NOT NULL UNIQUE,
    "password" VARCHAR(512) NOT NULL,
    "created" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

/**
 *  CREATE INDICIES
 */

-- DROP INDEX IF EXISTS "idx_client_apikey"

CREATE INDEX "idx_client_apikey"
    ON "client" USING BTREE("apikey");

-- DROP INDEX IF EXISTS "idx_credential_email_hash"

CREATE INDEX "idx_credential_email_hash"
    ON "credential" USING BTREE("email_hash");

COMMIT;

-------------------------------------------------------------------------
-- No CREATE or ALTER statements should be outside of the `COMMIT`.
-------------------------------------------------------------------------
