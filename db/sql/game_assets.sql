-- Table: public.game_assets

-- DROP TABLE IF EXISTS public.game_assets;

CREATE TABLE IF NOT EXISTS public.game_assets
(
    id integer NOT NULL DEFAULT nextval('game_assets_id_seq'::regclass),
    title character varying(255) COLLATE pg_catalog."default",
    file_path text COLLATE pg_catalog."default",
    web_url text COLLATE pg_catalog."default",
    software character varying(100)[] COLLATE pg_catalog."default",
    file_type character varying(255) COLLATE pg_catalog."default",
    note text COLLATE pg_catalog."default",
    keywords character varying(100)[] COLLATE pg_catalog."default",
    meta jsonb,
    score numeric(10,2),
    ctime timestamp without time zone,
    file_extension character varying(32)[] COLLATE pg_catalog."default",
    src integer,
    price integer,
    license integer,
    pics text[] COLLATE pg_catalog."default",
    pics_local text[] COLLATE pg_catalog."default",
    CONSTRAINT game_assets_pkey PRIMARY KEY (id)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.game_assets
    OWNER to postgres;
-- Index: idx_ctime

-- DROP INDEX IF EXISTS public.idx_ctime;

CREATE INDEX IF NOT EXISTS idx_ctime
    ON public.game_assets USING btree
    (ctime ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: idx_file_extension

-- DROP INDEX IF EXISTS public.idx_file_extension;

CREATE INDEX IF NOT EXISTS idx_file_extension
    ON public.game_assets USING btree
    (file_extension COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: idx_file_path

-- DROP INDEX IF EXISTS public.idx_file_path;

CREATE INDEX IF NOT EXISTS idx_file_path
    ON public.game_assets USING btree
    (file_path COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: idx_file_type

-- DROP INDEX IF EXISTS public.idx_file_type;

CREATE INDEX IF NOT EXISTS idx_file_type
    ON public.game_assets USING btree
    (file_type COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: idx_keywords

-- DROP INDEX IF EXISTS public.idx_keywords;

CREATE INDEX IF NOT EXISTS idx_keywords
    ON public.game_assets USING gin
    (keywords COLLATE pg_catalog."default")
    TABLESPACE pg_default;
-- Index: idx_meta

-- DROP INDEX IF EXISTS public.idx_meta;

CREATE INDEX IF NOT EXISTS idx_meta
    ON public.game_assets USING gin
    (meta)
    TABLESPACE pg_default;
-- Index: idx_score

-- DROP INDEX IF EXISTS public.idx_score;

CREATE INDEX IF NOT EXISTS idx_score
    ON public.game_assets USING btree
    (score ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: idx_software

-- DROP INDEX IF EXISTS public.idx_software;

CREATE INDEX IF NOT EXISTS idx_software
    ON public.game_assets USING gin
    (software COLLATE pg_catalog."default")
    TABLESPACE pg_default;
-- Index: idx_title

-- DROP INDEX IF EXISTS public.idx_title;

CREATE INDEX IF NOT EXISTS idx_title
    ON public.game_assets USING btree
    (title COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
-- Index: idx_web_url

-- DROP INDEX IF EXISTS public.idx_web_url;

CREATE INDEX IF NOT EXISTS idx_web_url
    ON public.game_assets USING btree
    (web_url COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;