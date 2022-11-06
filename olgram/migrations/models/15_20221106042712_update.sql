-- upgrade --
ALTER TABLE "bot" ADD "last_mailing_at" TIMESTAMPTZ;
ALTER TABLE "bot" ADD "enable_mailing" BOOL NOT NULL  DEFAULT False;
CREATE TABLE IF NOT EXISTS "mailinguser" (
    "id" BIGSERIAL NOT NULL PRIMARY KEY,
    "telegram_id" BIGINT NOT NULL,
    "bot_id" INT NOT NULL REFERENCES "bot" ("id") ON DELETE CASCADE,
    CONSTRAINT "uid_mailinguser_bot_id_906a76" UNIQUE ("bot_id", "telegram_id")
);
CREATE INDEX IF NOT EXISTS "idx_mailinguser_telegra_55de60" ON "mailinguser" ("telegram_id");;
-- downgrade --
ALTER TABLE "bot" DROP COLUMN "last_mailing_at";
ALTER TABLE "bot" DROP COLUMN "enable_mailing";
DROP TABLE IF EXISTS "mailinguser";
