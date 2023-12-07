-- Keep a log of any SQL queries you execute as you solve the mystery.

-- Find crime scene description
SELECT description
FROM crime_scene_reports
WHERE month = 7 AND day = 28 AND street = 'Humphrey Street';

-- Find transcripts of the interview and the person who is been interviewed
SELECT name, transcript
FROM interviews
WHERE month = 7 AND day = 28;

-- Find possible phone numbers on the phone calls (SUSPECTS LIST)
SELECT name, caller, receiver FROM people
JOIN phone_calls ON people.phone_number = phone_calls.caller
WHERE month = 7 AND day = 28 AND duration < 60;

-- Find destination for the earliest flight the day after the theft
SELECT city FROM airports
WHERE id = (SELECT destination_airport_id FROM flights WHERE month = 7 AND day = 29 ORDER BY hour LIMIT 1);

-- Find license plate of the thief car (SUSPECTS LIST)
SELECT name FROM people
JOIN bakery_security_logs ON people.license_plate = bakery_security_logs.license_plate
WHERE activity = 'exit' AND month = 7 AND day = 28 AND hour = 10 AND minute >= 15 AND minute <= 25;

-- Find transactions at the ATMs in the morning to find a possible account number (SUSPECTS LIST)
SELECT name FROM people
JOIN bank_accounts ON people.id = bank_accounts.person_id
JOIN atm_transactions ON bank_accounts.account_number = atm_transactions.account_number
WHERE month = 7 AND day = 28 AND transaction_type = 'withdraw' AND atm_location = 'Leggett Street';

-- Find the info of the car owner
SELECT * FROM people WHERE license_plate = (SELECT license_plate FROM bakery_security_logs WHERE activity = 'exit' AND month = 7 AND day = 28 AND hour = 10 AND minute >= 25);

-- Check if the car's owner is on the flight
SELECT * FROM passengers
WHERE passport_number = (SELECT passport_number FROM people WHERE license_plate = (SELECT license_plate FROM bakery_security_logs WHERE activity = 'exit' AND month = 7 AND day = 28 AND hour = 10 AND minute >= 25));

-- Get Taylor phone number
SELECT name, phone_number FROM people
WHERE passport_number = (SELECT passport_number FROM passengers WHERE passport_number = (SELECT passport_number FROM people WHERE license_plate = (SELECT license_plate FROM bakery_security_logs WHERE activity = 'exit' AND month = 7 AND day = 28 AND hour = 10 AND minute >= 25)));

-- Get call from Taylor after the theft
SELECT caller, receiver FROM phone_calls WHERE month = 7 AND day = 28 AND duration < 60 AND caller = (SELECT phone_number FROM people WHERE name = 'Taylor');

-- Get accomplice info
SELECT * FROM people WHERE phone_number = (SELECT receiver FROM phone_calls WHERE month = 7 AND day = 28 AND duration < 60 AND caller = (SELECT phone_number FROM people WHERE name = 'Taylor'));

-- Check Taylor withdraw
SELECT account_number, amount FROM atm_transactions
WHERE month = 7 AND day = 28 AND transaction_type = 'withdraw' AND atm_location = 'Leggett Street' AND account_number = (SELECT account_number FROM people JOIN bank_accounts ON people.id = bank_accounts.person_id WHERE name = 'Taylor');

-- Find passengers on the flight for New York City. All of them are suspects (SUSPECTS LIST)
SELECT name FROM people
JOIN passengers ON people.passport_number = passengers.passport_number
WHERE flight_id = (SELECT id FROM flights WHERE month = 7 AND day = 29 ORDER BY hour LIMIT 1);

-- Bruce appears in all the suspects lists.
-- Get the receivers of the calls
SELECT name, caller, receiver FROM people
JOIN phone_calls ON people.phone_number = phone_calls.receiver
WHERE month = 7 AND day = 28 AND duration < 60;
-- Bruce called Robin
