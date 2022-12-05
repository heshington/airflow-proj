

CREATE TABLE IF NOT EXISTS logs.landing_table (
    site character(50),
    start_timestamp timestamp without time zone,
    end_timestamp timestamp without time zone,
    id integer NOT NULL
);
ALTER TABLE logs.landing_table OWNER TO admin;

--
-- TOC entry 220 (class 1259 OID 32904)
-- Name: landing_table_id_seq; Type: SEQUENCE; Schema: logs; Owner: admin
--

CREATE SEQUENCE IF NOT EXISTS logs.landing_table_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- Empty out the table before copying from csv.
TRUNCATE LOGS.landing_table;
    




