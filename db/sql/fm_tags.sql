-- Table: public.fm_tags

-- DROP TABLE IF EXISTS public.fm_tags;

CREATE TABLE IF NOT EXISTS public.fm_tags
(
    id integer NOT NULL DEFAULT nextval('fm_tags_id_seq'::regclass),
    name character varying(255) COLLATE pg_catalog."default" NOT NULL,
    icon text COLLATE pg_catalog."default",
    CONSTRAINT fm_tags_pkey PRIMARY KEY (id),
    CONSTRAINT fm_tags_name_key UNIQUE (name)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.fm_tags
    OWNER to postgres;