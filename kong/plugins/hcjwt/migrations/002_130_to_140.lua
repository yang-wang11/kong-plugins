return {
  postgres = {
    up = [[
      DO $$
      BEGIN
        ALTER TABLE IF EXISTS ONLY hcjwt_secrets ADD tags TEXT[];
      EXCEPTION WHEN DUPLICATE_COLUMN THEN
        -- Do nothing, accept existing state
      END$$;

      DO $$
      BEGIN
        CREATE INDEX IF NOT EXISTS hcjwtsecrets_tags_idex_tags_idx ON hcjwt_secrets USING GIN(tags);
      EXCEPTION WHEN UNDEFINED_COLUMN THEN
        -- Do nothing, accept existing state
      END$$;

      DROP TRIGGER IF EXISTS hcjwtsecrets_sync_tags_trigger ON hcjwt_secrets;

      DO $$
      BEGIN
        CREATE TRIGGER hcjwtsecrets_sync_tags_trigger
        AFTER INSERT OR UPDATE OF tags OR DELETE ON hcjwt_secrets
        FOR EACH ROW
        EXECUTE PROCEDURE sync_tags();
      EXCEPTION WHEN UNDEFINED_COLUMN OR UNDEFINED_TABLE THEN
        -- Do nothing, accept existing state
      END$$;

    ]],
  },
}
