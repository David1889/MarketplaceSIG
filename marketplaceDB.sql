--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

-- Started on 2025-06-16 13:26:30

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'SQL_ASCII';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 2 (class 3079 OID 31273)
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- TOC entry 5855 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


--
-- TOC entry 1638 (class 1247 OID 32416)
-- Name: user_type; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.user_type AS ENUM (
    'client',
    'owner',
    'admin'
);


ALTER TYPE public.user_type OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 218 (class 1259 OID 31268)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- TOC entry 229 (class 1259 OID 32453)
-- Name: product; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    price double precision NOT NULL,
    has_discount boolean,
    shop_id integer NOT NULL
);


ALTER TABLE public.product OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 32452)
-- Name: product_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_id_seq OWNER TO postgres;

--
-- TOC entry 5856 (class 0 OID 0)
-- Dependencies: 228
-- Name: product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.product_id_seq OWNED BY public.product.id;


--
-- TOC entry 227 (class 1259 OID 32437)
-- Name: shop; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.shop (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    coordinates public.geography(Point,4326),
    user_id integer NOT NULL
);


ALTER TABLE public.shop OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 32436)
-- Name: shop_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.shop_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.shop_id_seq OWNER TO postgres;

--
-- TOC entry 5857 (class 0 OID 0)
-- Dependencies: 226
-- Name: shop_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.shop_id_seq OWNED BY public.shop.id;


--
-- TOC entry 225 (class 1259 OID 32424)
-- Name: user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    email character varying(100) NOT NULL,
    password character varying(100) NOT NULL,
    type public.user_type NOT NULL,
    coordinates public.geography(Point,4326),
    radius double precision
);


ALTER TABLE public."user" OWNER TO postgres;

--
-- TOC entry 224 (class 1259 OID 32423)
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_id_seq OWNER TO postgres;

--
-- TOC entry 5858 (class 0 OID 0)
-- Dependencies: 224
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- TOC entry 5673 (class 2604 OID 32456)
-- Name: product id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product ALTER COLUMN id SET DEFAULT nextval('public.product_id_seq'::regclass);


--
-- TOC entry 5672 (class 2604 OID 32440)
-- Name: shop id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shop ALTER COLUMN id SET DEFAULT nextval('public.shop_id_seq'::regclass);


--
-- TOC entry 5671 (class 2604 OID 32427)
-- Name: user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- TOC entry 5843 (class 0 OID 31268)
-- Dependencies: 218
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
3c562a00a556
\.


--
-- TOC entry 5849 (class 0 OID 32453)
-- Dependencies: 229
-- Data for Name: product; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.product (id, name, price, has_discount, shop_id) FROM stdin;
1	Producto1 Modificado	120.75	f	1
\.


--
-- TOC entry 5847 (class 0 OID 32437)
-- Dependencies: 227
-- Data for Name: shop; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.shop (id, name, coordinates, user_id) FROM stdin;
1	Tienda1 Modificada	0101000020E610000014AE47E17A344DC0AE47E17A144E41C0	3
2	Tienda Canalla	0101000020E610000098721992EE514EC00096F0DF177940C0	2
3	Tienda Canalla	0101000020E610000098721992EE514EC00096F0DF177940C0	3
4	Tienda Canalla	0101000020E610000098721992EE514EC00096F0DF177940C0	3
5	Tienda Canalla	0101000020E610000098721992EE514EC00096F0DF177940C0	3
\.


--
-- TOC entry 5670 (class 0 OID 31595)
-- Dependencies: 220
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- TOC entry 5845 (class 0 OID 32424)
-- Dependencies: 225
-- Data for Name: user; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."user" (id, name, email, password, type, coordinates, radius) FROM stdin;
1	Test User	test@example.com	1234	client	\N	5
2	David	david@mail.com	1234	client	\N	5
3	David	davidowner@mail.com	1234	owner	\N	5
\.


--
-- TOC entry 5859 (class 0 OID 0)
-- Dependencies: 228
-- Name: product_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.product_id_seq', 1, true);


--
-- TOC entry 5860 (class 0 OID 0)
-- Dependencies: 226
-- Name: shop_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.shop_id_seq', 5, true);


--
-- TOC entry 5861 (class 0 OID 0)
-- Dependencies: 224
-- Name: user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_id_seq', 3, true);


--
-- TOC entry 5676 (class 2606 OID 31272)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- TOC entry 5690 (class 2606 OID 32458)
-- Name: product product_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_pkey PRIMARY KEY (id);


--
-- TOC entry 5688 (class 2606 OID 32444)
-- Name: shop shop_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shop
    ADD CONSTRAINT shop_pkey PRIMARY KEY (id);


--
-- TOC entry 5682 (class 2606 OID 32433)
-- Name: user user_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_email_key UNIQUE (email);


--
-- TOC entry 5684 (class 2606 OID 32431)
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- TOC entry 5685 (class 1259 OID 32451)
-- Name: idx_shop_coordinate; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_shop_coordinate ON public.shop USING gist (coordinates);


--
-- TOC entry 5686 (class 1259 OID 32450)
-- Name: idx_shop_coordinates; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_shop_coordinates ON public.shop USING gist (coordinates);


--
-- TOC entry 5679 (class 1259 OID 32435)
-- Name: idx_user_coordinate; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_coordinate ON public."user" USING gist (coordinates);


--
-- TOC entry 5680 (class 1259 OID 32434)
-- Name: idx_user_coordinates; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_user_coordinates ON public."user" USING gist (coordinates);


--
-- TOC entry 5692 (class 2606 OID 32459)
-- Name: product product_shop_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_shop_id_fkey FOREIGN KEY (shop_id) REFERENCES public.shop(id);


--
-- TOC entry 5691 (class 2606 OID 32445)
-- Name: shop shop_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.shop
    ADD CONSTRAINT shop_user_id_fkey FOREIGN KEY (user_id) REFERENCES public."user"(id);


-- Completed on 2025-06-16 13:26:31

--
-- PostgreSQL database dump complete
--

