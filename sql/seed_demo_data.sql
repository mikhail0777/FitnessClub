--
-- PostgreSQL database dump
--

\restrict BM5ctCVzcSItkn2cKUw4rRmeguE0ljjzmPlR23wZN8gO6GyhItuQIChCzCRaCLb

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

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
-- Data for Name: equipment; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.equipment VALUES (1, 1, 'Treadmill #1', 'operational', NULL, 1, 1);
INSERT INTO public.equipment VALUES (2, 1, 'Treadmill #2', 'out_of_order', NULL, 1, 1);
INSERT INTO public.equipment VALUES (3, 2, 'Rowing Machine #1', 'operational', NULL, 1, 1);
INSERT INTO public.equipment VALUES (4, NULL, 'Barbell', 'operational', 'Strength', 10, 10);
INSERT INTO public.equipment VALUES (5, NULL, 'Dumbbell Set (5–50 lb)', 'operational', 'Strength', 20, 20);
INSERT INTO public.equipment VALUES (6, NULL, 'Kettlebell (various sizes)', 'operational', 'Strength', 15, 15);
INSERT INTO public.equipment VALUES (7, NULL, 'Bench Press', 'operational', 'Strength', 4, 4);
INSERT INTO public.equipment VALUES (8, NULL, 'Squat Rack', 'operational', 'Strength', 3, 3);
INSERT INTO public.equipment VALUES (9, NULL, 'Smith Machine', 'operational', 'Strength', 2, 2);
INSERT INTO public.equipment VALUES (10, NULL, 'Leg Press Machine', 'operational', 'Strength', 2, 2);
INSERT INTO public.equipment VALUES (11, NULL, 'Cable Machine', 'operational', 'Strength', 3, 3);
INSERT INTO public.equipment VALUES (12, NULL, 'Pull-Up Bar', 'operational', 'Strength', 6, 6);
INSERT INTO public.equipment VALUES (14, NULL, 'Stationary Bike', 'operational', 'Cardio', 5, 5);
INSERT INTO public.equipment VALUES (15, NULL, 'Rowing Machine', 'operational', 'Cardio', 4, 4);
INSERT INTO public.equipment VALUES (16, NULL, 'Elliptical Machine', 'operational', 'Cardio', 4, 4);
INSERT INTO public.equipment VALUES (17, NULL, 'Stair Climber', 'operational', 'Cardio', 3, 3);
INSERT INTO public.equipment VALUES (18, NULL, 'Resistance Band Set', 'operational', 'Accessories', 20, 20);
INSERT INTO public.equipment VALUES (19, NULL, 'Medicine Ball (various weights)', 'operational', 'Accessories', 10, 10);
INSERT INTO public.equipment VALUES (20, NULL, 'Jump Rope', 'operational', 'Accessories', 15, 15);
INSERT INTO public.equipment VALUES (21, NULL, 'Yoga Mat', 'operational', 'Accessories', 25, 25);
INSERT INTO public.equipment VALUES (22, NULL, 'Foam Roller', 'operational', 'Accessories', 12, 12);
INSERT INTO public.equipment VALUES (23, NULL, 'Weight Belt', 'operational', 'Accessories', 10, 10);
INSERT INTO public.equipment VALUES (24, NULL, 'Ankle Weights', 'operational', 'Accessories', 8, 8);
INSERT INTO public.equipment VALUES (13, NULL, 'Treadmill', 'operational', 'Cardio', 6, 6);


--
-- Data for Name: members; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.members VALUES (9, 'Bob Smith', 'bob@example.com', '1990-07-21', 'M', '555-123-0001', '2025-12-08 00:19:54.740109-05');
INSERT INTO public.members VALUES (10, 'Mary Johnson', 'maryj@example.com', '1995-02-14', 'F', '555-123-0002', '2025-12-08 00:19:54.740109-05');
INSERT INTO public.members VALUES (11, 'Alex Brown', 'alexb@example.com', '1988-09-08', 'M', '555-123-0003', '2025-12-08 00:19:54.740109-05');
INSERT INTO public.members VALUES (12, 'Sarah Kim', 'sarahk@example.com', '1997-11-30', 'F', '555-123-0004', '2025-12-08 00:19:54.740109-05');
INSERT INTO public.members VALUES (13, 'John Carter', 'johnc@example.com', '1992-05-19', 'M', '555-123-0005', '2025-12-08 00:19:54.740109-05');
INSERT INTO public.members VALUES (14, 'Emily Davis', 'emilyd@example.com', '2000-01-01', 'F', '555-123-0006', '2025-12-08 00:19:54.740109-05');


--
-- Data for Name: equipment_rentals; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.equipment_rentals VALUES (1, 11, 13, '2025-12-08', '2025-12-09', '2025-12-08');


--
-- Data for Name: trainers; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.trainers VALUES (1, 'Coach Chris', 'chris.trainer@example.com', 'Strength', '555-4444', '2025-11-30');
INSERT INTO public.trainers VALUES (2, 'Coach Dana', 'dana.trainer@example.com', 'Cardio', '555-5555', '2025-11-30');
INSERT INTO public.trainers VALUES (4, 'Bob Trainer', 'bob.trainer@example.com', 'Strength & Conditioning', NULL, '2025-12-08');
INSERT INTO public.trainers VALUES (5, 'Mary Coach', 'mary.coach@example.com', 'Weight Loss', NULL, '2025-12-08');
INSERT INTO public.trainers VALUES (6, 'Alex PT', 'alex.pt@example.com', 'Athletic Performance', NULL, '2025-12-08');


--
-- Data for Name: personal_training_sessions; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.personal_training_sessions VALUES (1, 11, 4, '2025-12-08', '12:00:00', 'scheduled');
INSERT INTO public.personal_training_sessions VALUES (2, 13, 2, '2025-08-12', '12:00:00', 'scheduled');


--
-- Name: equipment_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.equipment_id_seq', 24, true);


--
-- Name: equipment_rentals_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.equipment_rentals_id_seq', 1, true);


--
-- Name: members_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.members_id_seq', 14, true);


--
-- Name: personal_training_sessions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.personal_training_sessions_id_seq', 2, true);


--
-- Name: trainers_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.trainers_id_seq', 6, true);


--
-- PostgreSQL database dump complete
--

\unrestrict BM5ctCVzcSItkn2cKUw4rRmeguE0ljjzmPlR23wZN8gO6GyhItuQIChCzCRaCLb

