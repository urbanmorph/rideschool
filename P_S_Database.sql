--
-- PostgreSQL database dump
--

-- Dumped from database version 15.3
-- Dumped by pg_dump version 15.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: update_participant_updated_at(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_participant_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.participant_updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_participant_updated_at() OWNER TO postgres;

--
-- Name: update_session_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_session_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.session_updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_session_updated_at_column() OWNER TO postgres;

--
-- Name: update_session_updated_datetime(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_session_updated_datetime() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.session_updated_datetime = current_timestamp;
  RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_session_updated_datetime() OWNER TO postgres;

--
-- Name: update_timestamp(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_timestamp() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
  BEGIN
    NEW.updated_datetime := current_timestamp;
    RETURN NEW;
  END;
$$;


ALTER FUNCTION public.update_timestamp() OWNER TO postgres;

--
-- Name: update_trainer_updated_at(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_trainer_updated_at() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.trainer_updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_trainer_updated_at() OWNER TO postgres;

--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
  NEW.updated_at = CURRENT_TIMESTAMP;
  RETURN NEW;
END;
$$;


ALTER FUNCTION public.update_updated_at_column() OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: organisation; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.organisation (
    organisation_id integer NOT NULL,
    organisation_name character varying(255),
    organisation_address character varying(255),
    organisation_contact character varying(255),
    organisation_email character varying(255),
    organisation_type character varying(255),
    organisation_activities character varying(255),
    organisation_legal_status_document bytea,
    coordinator_name character varying(255),
    coordinator_email character varying(255),
    organisation_created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    organisation_updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.organisation OWNER TO postgres;

--
-- Name: organisation_organisation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.organisation_organisation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.organisation_organisation_id_seq OWNER TO postgres;

--
-- Name: organisation_organisation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.organisation_organisation_id_seq OWNED BY public.organisation.organisation_id;


--
-- Name: participants; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.participants (
    participant_id integer NOT NULL,
    participant_name character varying(255) NOT NULL,
    participant_email character varying(255),
    participant_contact character varying(20),
    participant_address text,
    participant_age character varying(10),
    participant_gender character varying(255),
    training_location_id integer,
    participant_created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    participant_updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    participant_status character varying(20) DEFAULT 'new'::character varying,
    participant_created_date timestamp without time zone,
    participant_updated_date timestamp without time zone,
    CONSTRAINT participants_participant_status_check CHECK (((participant_status)::text = ANY ((ARRAY['NEW'::character varying, 'ONGOING'::character varying, 'COMPLETED'::character varying])::text[])))
);


ALTER TABLE public.participants OWNER TO postgres;

--
-- Name: participants_participant_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.participants_participant_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.participants_participant_id_seq OWNER TO postgres;

--
-- Name: participants_participant_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.participants_participant_id_seq OWNED BY public.participants.participant_id;


--
-- Name: sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sessions (
    session_id integer NOT NULL,
    participant_name text,
    trainer_name text,
    scheduled_datetime timestamp without time zone,
    actual_datetime timestamp without time zone,
    hours_trained double precision,
    picture_path text,
    video_path text,
    description text,
    session_current_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    session_update_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.sessions OWNER TO postgres;

--
-- Name: sessions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.sessions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.sessions_id_seq OWNER TO postgres;

--
-- Name: sessions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.sessions_id_seq OWNED BY public.sessions.session_id;


--
-- Name: trainer; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trainer (
    trainer_id integer NOT NULL,
    trainer_name character varying(255) NOT NULL,
    trainer_email character varying(255),
    trainer_contact integer,
    trainer_address text,
    trainer_age interval year,
    trainer_gender character varying(255),
    trainer_education character varying(255),
    trainer_aadhar_no character varying(255),
    trainer_created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    trainer_updated_at timestamp without time zone,
    trainer_training_completion_date date NOT NULL,
    training_location_id integer,
    organisation_id integer,
    trainer_language text[]
);


ALTER TABLE public.trainer OWNER TO postgres;

--
-- Name: trainer_trainer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trainer_trainer_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.trainer_trainer_id_seq OWNER TO postgres;

--
-- Name: trainer_trainer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trainer_trainer_id_seq OWNED BY public.trainer.trainer_id;


--
-- Name: trainers_availability; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trainers_availability (
    trainer_id integer,
    blocked_date date,
    availability_time_range tsrange
);


ALTER TABLE public.trainers_availability OWNER TO postgres;

--
-- Name: training_locations_list; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.training_locations_list (
    training_location_id integer NOT NULL,
    training_location character varying(255),
    training_location_address character varying(255),
    training_location_latitude double precision,
    training_location_longitude double precision,
    training_location_created timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    training_location_updated timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.training_locations_list OWNER TO postgres;

--
-- Name: organisation organisation_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organisation ALTER COLUMN organisation_id SET DEFAULT nextval('public.organisation_organisation_id_seq'::regclass);


--
-- Name: participants participant_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.participants ALTER COLUMN participant_id SET DEFAULT nextval('public.participants_participant_id_seq'::regclass);


--
-- Name: sessions session_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sessions ALTER COLUMN session_id SET DEFAULT nextval('public.sessions_id_seq'::regclass);


--
-- Name: trainer trainer_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trainer ALTER COLUMN trainer_id SET DEFAULT nextval('public.trainer_trainer_id_seq'::regclass);


--
-- Data for Name: organisation; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.organisation (organisation_id, organisation_name, organisation_address, organisation_contact, organisation_email, organisation_type, organisation_activities, organisation_legal_status_document, coordinator_name, coordinator_email, organisation_created_at, organisation_updated_at) FROM stdin;
1111	abc	abc 3rd cross	0909090987	abc@g.in	private	avc	\N	\N	\N	2023-07-10 22:03:46.15265	2023-07-10 22:03:46.15265
\.


--
-- Data for Name: participants; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.participants (participant_id, participant_name, participant_email, participant_contact, participant_address, participant_age, participant_gender, training_location_id, participant_created_at, participant_updated_at, participant_status, participant_created_date, participant_updated_date) FROM stdin;
\.


--
-- Data for Name: sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sessions (session_id, participant_name, trainer_name, scheduled_datetime, actual_datetime, hours_trained, picture_path, video_path, description, session_current_date, session_update_date) FROM stdin;
\.


--
-- Data for Name: trainer; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trainer (trainer_id, trainer_name, trainer_email, trainer_contact, trainer_address, trainer_age, trainer_gender, trainer_education, trainer_aadhar_no, trainer_created_at, trainer_updated_at, trainer_training_completion_date, training_location_id, organisation_id, trainer_language) FROM stdin;
\.


--
-- Data for Name: trainers_availability; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.trainers_availability (trainer_id, blocked_date, availability_time_range) FROM stdin;
\.


--
-- Data for Name: training_locations_list; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.training_locations_list (training_location_id, training_location, training_location_address, training_location_latitude, training_location_longitude, training_location_created, training_location_updated) FROM stdin;
\.


--
-- Name: organisation_organisation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.organisation_organisation_id_seq', 1, false);


--
-- Name: participants_participant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.participants_participant_id_seq', 79, true);


--
-- Name: sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sessions_id_seq', 1, false);


--
-- Name: trainer_trainer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trainer_trainer_id_seq', 17, true);


--
-- Name: organisation organisation_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.organisation
    ADD CONSTRAINT organisation_pkey PRIMARY KEY (organisation_id);


--
-- Name: participants participants_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.participants
    ADD CONSTRAINT participants_pkey PRIMARY KEY (participant_id);


--
-- Name: sessions sessions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sessions
    ADD CONSTRAINT sessions_pkey PRIMARY KEY (session_id);


--
-- Name: trainer trainer_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trainer
    ADD CONSTRAINT trainer_pkey PRIMARY KEY (trainer_id);


--
-- Name: training_locations_list training_locations_list_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.training_locations_list
    ADD CONSTRAINT training_locations_list_pkey PRIMARY KEY (training_location_id);


--
-- Name: trainer trainer_updated_at_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trainer_updated_at_trigger BEFORE UPDATE ON public.trainer FOR EACH ROW EXECUTE FUNCTION public.update_trainer_updated_at();


--
-- Name: participants update_participant_updated_at_trigger; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER update_participant_updated_at_trigger BEFORE UPDATE ON public.participants FOR EACH ROW EXECUTE FUNCTION public.update_participant_updated_at();


--
-- Name: trainers_availability trainers_availability_trainer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trainers_availability
    ADD CONSTRAINT trainers_availability_trainer_id_fkey FOREIGN KEY (trainer_id) REFERENCES public.trainer(trainer_id);


--
-- PostgreSQL database dump complete
--

