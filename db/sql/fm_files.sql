-- Table: public.fm_files

-- DROP TABLE IF EXISTS public.fm_files;

CREATE TABLE IF NOT EXISTS public.fm_files
(
    id integer NOT NULL DEFAULT nextval('fm_files_id_seq'::regclass),
    path text COLLATE pg_catalog."default" NOT NULL,
    alias character varying(255) COLLATE pg_catalog."default" NOT NULL,
    tags character varying(255) COLLATE pg_catalog."default",
    CONSTRAINT fm_files_pkey PRIMARY KEY (id),
    CONSTRAINT unique_file UNIQUE (path, alias)
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.fm_files
    OWNER to postgres;