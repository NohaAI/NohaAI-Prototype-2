--
-- PostgreSQL database dump
--

-- Dumped from database version 17.2
-- Dumped by pg_dump version 17.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pgagent; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA pgagent;


ALTER SCHEMA pgagent OWNER TO postgres;

--
-- Name: SCHEMA pgagent; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA pgagent IS 'pgAgent system tables';


--
-- Name: pgagent; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgagent WITH SCHEMA pgagent;


--
-- Name: EXTENSION pgagent; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgagent IS 'A PostgreSQL job scheduler';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: chat_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_history (
    chat_history_id integer NOT NULL,
    interview_id integer,
    question_id integer,
    candidate_answer text
);


ALTER TABLE public.chat_history OWNER TO postgres;

--
-- Name: chat_history_chat_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chat_history_chat_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chat_history_chat_history_id_seq OWNER TO postgres;

--
-- Name: chat_history_chat_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chat_history_chat_history_id_seq OWNED BY public.chat_history.chat_history_id;


--
-- Name: final_evaluations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.final_evaluations (
    final_evaluation_id integer NOT NULL,
    interview_id integer,
    final_evaluation_json text,
    final_feedback text
);


ALTER TABLE public.final_evaluations OWNER TO postgres;

--
-- Name: final_evaluations_final_evaluation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.final_evaluations_final_evaluation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.final_evaluations_final_evaluation_id_seq OWNER TO postgres;

--
-- Name: final_evaluations_final_evaluation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.final_evaluations_final_evaluation_id_seq OWNED BY public.final_evaluations.final_evaluation_id;


--
-- Name: interview_question_evaluations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interview_question_evaluations (
    question_evaluation_id integer NOT NULL,
    interview_id integer,
    question_id integer,
    score numeric(5,2),
    question_evaluation_json text
);


ALTER TABLE public.interview_question_evaluations OWNER TO postgres;

--
-- Name: interview_question_evaluations_question_evaluation_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.interview_question_evaluations_question_evaluation_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.interview_question_evaluations_question_evaluation_id_seq OWNER TO postgres;

--
-- Name: interview_question_evaluations_question_evaluation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.interview_question_evaluations_question_evaluation_id_seq OWNED BY public.interview_question_evaluations.question_evaluation_id;


--
-- Name: interview_questions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interview_questions (
    interview_id integer NOT NULL,
    question_id integer NOT NULL
);


ALTER TABLE public.interview_questions OWNER TO postgres;

--
-- Name: interviews; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.interviews (
    interview_id integer NOT NULL,
    user_id integer,
    interview_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    interview_recording_url text
);


ALTER TABLE public.interviews OWNER TO postgres;

--
-- Name: interviews_interview_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.interviews_interview_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.interviews_interview_id_seq OWNER TO postgres;

--
-- Name: interviews_interview_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.interviews_interview_id_seq OWNED BY public.interviews.interview_id;


--
-- Name: metric_categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.metric_categories (
    category_id integer NOT NULL,
    metric_category text,
    question_type_id integer,
    question_id integer
);


ALTER TABLE public.metric_categories OWNER TO postgres;

--
-- Name: metric_categories_category_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.metric_categories_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.metric_categories_category_id_seq OWNER TO postgres;

--
-- Name: metric_categories_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.metric_categories_category_id_seq OWNED BY public.metric_categories.category_id;


--
-- Name: metric_subcategories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.metric_subcategories (
    subcategory_id integer NOT NULL,
    metric_subcategory character varying(255) NOT NULL,
    category_id integer,
    question_id integer
);


ALTER TABLE public.metric_subcategories OWNER TO postgres;

--
-- Name: metric_subcategories_subcategory_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.metric_subcategories_subcategory_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.metric_subcategories_subcategory_id_seq OWNER TO postgres;

--
-- Name: metric_subcategories_subcategory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.metric_subcategories_subcategory_id_seq OWNED BY public.metric_subcategories.subcategory_id;


--
-- Name: questions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.questions (
    question_id integer NOT NULL,
    question text NOT NULL,
    question_type character varying(100),
    question_type_id integer
);


ALTER TABLE public.questions OWNER TO postgres;

--
-- Name: questions_question_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.questions_question_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.questions_question_id_seq OWNER TO postgres;

--
-- Name: questions_question_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.questions_question_id_seq OWNED BY public.questions.question_id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    name character varying(255) NOT NULL
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_user_id_seq OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: chat_history chat_history_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_history ALTER COLUMN chat_history_id SET DEFAULT nextval('public.chat_history_chat_history_id_seq'::regclass);


--
-- Name: final_evaluations final_evaluation_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.final_evaluations ALTER COLUMN final_evaluation_id SET DEFAULT nextval('public.final_evaluations_final_evaluation_id_seq'::regclass);


--
-- Name: interview_question_evaluations question_evaluation_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interview_question_evaluations ALTER COLUMN question_evaluation_id SET DEFAULT nextval('public.interview_question_evaluations_question_evaluation_id_seq'::regclass);


--
-- Name: interviews interview_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interviews ALTER COLUMN interview_id SET DEFAULT nextval('public.interviews_interview_id_seq'::regclass);


--
-- Name: metric_categories category_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.metric_categories ALTER COLUMN category_id SET DEFAULT nextval('public.metric_categories_category_id_seq'::regclass);


--
-- Name: metric_subcategories subcategory_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.metric_subcategories ALTER COLUMN subcategory_id SET DEFAULT nextval('public.metric_subcategories_subcategory_id_seq'::regclass);


--
-- Name: questions question_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questions ALTER COLUMN question_id SET DEFAULT nextval('public.questions_question_id_seq'::regclass);


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);


--
-- Data for Name: pga_jobagent; Type: TABLE DATA; Schema: pgagent; Owner: postgres
--

COPY pgagent.pga_jobagent (jagpid, jaglogintime, jagstation) FROM stdin;
8668	2024-12-07 01:44:33.186857+05:30	DESKTOP-QS068UM
\.


--
-- Data for Name: pga_jobclass; Type: TABLE DATA; Schema: pgagent; Owner: postgres
--

COPY pgagent.pga_jobclass (jclid, jclname) FROM stdin;
\.


--
-- Data for Name: pga_job; Type: TABLE DATA; Schema: pgagent; Owner: postgres
--

COPY pgagent.pga_job (jobid, jobjclid, jobname, jobdesc, jobhostagent, jobenabled, jobcreated, jobchanged, jobagentid, jobnextrun, joblastrun) FROM stdin;
\.


--
-- Data for Name: pga_schedule; Type: TABLE DATA; Schema: pgagent; Owner: postgres
--

COPY pgagent.pga_schedule (jscid, jscjobid, jscname, jscdesc, jscenabled, jscstart, jscend, jscminutes, jschours, jscweekdays, jscmonthdays, jscmonths) FROM stdin;
\.


--
-- Data for Name: pga_exception; Type: TABLE DATA; Schema: pgagent; Owner: postgres
--

COPY pgagent.pga_exception (jexid, jexscid, jexdate, jextime) FROM stdin;
\.


--
-- Data for Name: pga_joblog; Type: TABLE DATA; Schema: pgagent; Owner: postgres
--

COPY pgagent.pga_joblog (jlgid, jlgjobid, jlgstatus, jlgstart, jlgduration) FROM stdin;
\.


--
-- Data for Name: pga_jobstep; Type: TABLE DATA; Schema: pgagent; Owner: postgres
--

COPY pgagent.pga_jobstep (jstid, jstjobid, jstname, jstdesc, jstenabled, jstkind, jstcode, jstconnstr, jstdbname, jstonerror, jscnextrun) FROM stdin;
\.


--
-- Data for Name: pga_jobsteplog; Type: TABLE DATA; Schema: pgagent; Owner: postgres
--

COPY pgagent.pga_jobsteplog (jslid, jsljlgid, jsljstid, jslstatus, jslresult, jslstart, jslduration, jsloutput) FROM stdin;
\.


--
-- Data for Name: chat_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chat_history (chat_history_id, interview_id, question_id, candidate_answer) FROM stdin;
\.


--
-- Data for Name: final_evaluations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.final_evaluations (final_evaluation_id, interview_id, final_evaluation_json, final_feedback) FROM stdin;
2	2	{"overall": "strong", "recommendation": "hire"}	Good problem-solving abilities.
3	3	{"overall": "average", "recommendation": "consider"}	Efficient DSA solutions.
7	1	this is a JSON	\N
\.


--
-- Data for Name: interview_question_evaluations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.interview_question_evaluations (question_evaluation_id, interview_id, question_id, score, question_evaluation_json) FROM stdin;
3	3	3	4.30	{"approach": "efficient", "accuracy": "high"}
\.


--
-- Data for Name: interview_questions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.interview_questions (interview_id, question_id) FROM stdin;
3	3
3	7
\.


--
-- Data for Name: interviews; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.interviews (interview_id, user_id, interview_date, interview_recording_url) FROM stdin;
2	2	2024-12-02 11:30:00	https://recordings.example.com/bob_interview.mp3
3	3	2024-12-03 09:45:00	https://recordings.example.com/charlie_interview.mp3
1	1	2024-12-07 16:19:28.906	updated URL
4	1	2024-12-01 10:00:00	test_url
\.


--
-- Data for Name: metric_categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.metric_categories (category_id, metric_category, question_type_id, question_id) FROM stdin;
2	System Design	1	3
1	updated category	1	3
3	did the candidate consider edge case	1	7
\.


--
-- Data for Name: metric_subcategories; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.metric_subcategories (subcategory_id, metric_subcategory, category_id, question_id) FROM stdin;
8	Bug Frequency	2	7
9	Version Control Usage	4	7
6	this is updated subcategory	1	7
7	updated subcategory	2	7
11	string	1	7
12	string	1	7
\.


--
-- Data for Name: questions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.questions (question_id, question, question_type, question_type_id) FROM stdin;
3	What is the time complexity of quicksort in the worst case?	DSA	1
6	What is the difference between a stack and a queue?	DSA	1
7	Explain how a binary search works.	DSA	1
8	What is the time complexity of quicksort in the worst case?	DSA	1
9	How would you detect a cycle in a linked list?	DSA	1
10	What is the difference between depth-first search (DFS) and breadth-first search (BFS)?	DSA	1
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (user_id, name) FROM stdin;
2	Bob Smith
3	Charlie Davis
4	Diana Adams
1	Toyesh
5	user5
\.


--
-- Name: chat_history_chat_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.chat_history_chat_history_id_seq', 1, false);


--
-- Name: final_evaluations_final_evaluation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.final_evaluations_final_evaluation_id_seq', 7, true);


--
-- Name: interview_question_evaluations_question_evaluation_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.interview_question_evaluations_question_evaluation_id_seq', 5, true);


--
-- Name: interviews_interview_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.interviews_interview_id_seq', 5, true);


--
-- Name: metric_categories_category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.metric_categories_category_id_seq', 3, true);


--
-- Name: metric_subcategories_subcategory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.metric_subcategories_subcategory_id_seq', 12, true);


--
-- Name: questions_question_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.questions_question_id_seq', 10, true);


--
-- Name: users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_user_id_seq', 5, true);


--
-- Name: chat_history chat_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_history
    ADD CONSTRAINT chat_history_pkey PRIMARY KEY (chat_history_id);


--
-- Name: final_evaluations final_evaluations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.final_evaluations
    ADD CONSTRAINT final_evaluations_pkey PRIMARY KEY (final_evaluation_id);


--
-- Name: interview_question_evaluations interview_question_evaluations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interview_question_evaluations
    ADD CONSTRAINT interview_question_evaluations_pkey PRIMARY KEY (question_evaluation_id);


--
-- Name: interview_questions interview_questions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interview_questions
    ADD CONSTRAINT interview_questions_pkey PRIMARY KEY (interview_id, question_id);


--
-- Name: interviews interviews_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interviews
    ADD CONSTRAINT interviews_pkey PRIMARY KEY (interview_id);


--
-- Name: metric_categories metric_categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.metric_categories
    ADD CONSTRAINT metric_categories_pkey PRIMARY KEY (category_id);


--
-- Name: metric_subcategories metric_subcategories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.metric_subcategories
    ADD CONSTRAINT metric_subcategories_pkey PRIMARY KEY (subcategory_id);


--
-- Name: questions questions_composite_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_composite_unique UNIQUE (question_type_id, question_id);


--
-- Name: questions questions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questions
    ADD CONSTRAINT questions_pkey PRIMARY KEY (question_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: chat_history chat_history_interview_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_history
    ADD CONSTRAINT chat_history_interview_id_fkey FOREIGN KEY (interview_id) REFERENCES public.interviews(interview_id) ON DELETE CASCADE;


--
-- Name: chat_history chat_history_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_history
    ADD CONSTRAINT chat_history_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(question_id) ON DELETE CASCADE;


--
-- Name: final_evaluations final_evaluations_interview_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.final_evaluations
    ADD CONSTRAINT final_evaluations_interview_id_fkey FOREIGN KEY (interview_id) REFERENCES public.interviews(interview_id) ON DELETE CASCADE;


--
-- Name: interview_question_evaluations interview_question_evaluations_interview_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interview_question_evaluations
    ADD CONSTRAINT interview_question_evaluations_interview_id_fkey FOREIGN KEY (interview_id) REFERENCES public.interviews(interview_id) ON DELETE CASCADE;


--
-- Name: interview_question_evaluations interview_question_evaluations_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interview_question_evaluations
    ADD CONSTRAINT interview_question_evaluations_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(question_id) ON DELETE CASCADE;


--
-- Name: interview_questions interview_questions_interview_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interview_questions
    ADD CONSTRAINT interview_questions_interview_id_fkey FOREIGN KEY (interview_id) REFERENCES public.interviews(interview_id) ON DELETE CASCADE;


--
-- Name: interview_questions interview_questions_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interview_questions
    ADD CONSTRAINT interview_questions_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(question_id) ON DELETE CASCADE;


--
-- Name: interviews interviews_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.interviews
    ADD CONSTRAINT interviews_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id) ON DELETE CASCADE;


--
-- Name: metric_categories metric_categories_question_id_question_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.metric_categories
    ADD CONSTRAINT metric_categories_question_id_question_type_id_fkey FOREIGN KEY (question_id, question_type_id) REFERENCES public.questions(question_id, question_type_id);


--
-- Name: metric_subcategories metric_subcategories_question_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.metric_subcategories
    ADD CONSTRAINT metric_subcategories_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(question_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

