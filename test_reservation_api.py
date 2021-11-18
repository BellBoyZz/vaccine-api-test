""" Testing the Reservation API endpoint for the World Class Government group"""
import unittest
import requests
from decouple import config

HOST = config('URL')
reservation_URL = HOST + "/reservation"
registration_URL = HOST + "/registration"
FEEDBACK = {
    'success_reservation': 'reservation success!',
    'success_registration': 'registration success!',
    'missing_attribute': 'reservation failed: missing some attribute',
    'reserved': 'reservation failed: there is already a reservation for this citizen',
    'invalid_citizen_id': 'reservation failed: invalid citizen ID',
    'not_registered': 'reservation failed: citizen ID is not registered',
    'invalid_vaccine_name': 'reservation failed: invalid vaccine name'
}


class ReservationTest(unittest.TestCase):
    """
    Class for unit testing the Reservation API for the website wcg-apis-test.herokuapp.com (World Class Government) group

    @author Peerasu Watanasirang
    """

    def setUp(self):
        # default info to make a registration
        self.citizen_registration = self.create_citizen_info()

        # default info to make a reservation
        self.citizen_reservation = self.create_citizen_reservation_info()

        # delete that citizen if that citizen already exist
        requests.delete(registration_URL+'/'+self.citizen_registration["citizen_id"])

        # missing some attributes
        self.missing_attribute = [
            self.create_citizen_reservation_info(citizen_id=""),
            self.create_citizen_reservation_info(site_name="")
        ]

        # citizen_id is not the number of exact 13 digits
        self.invalid_citizen_id = [
            self.create_citizen_reservation_info(citizen_id="123"),  # 3 digits
            self.create_citizen_reservation_info(citizen_id="12345678901234567890"),  # 20 digits
            self.create_citizen_reservation_info(citizen_id="1abc2bcd3"),  # contain alphabets
            self.create_citizen_reservation_info(citizen_id="112233.44")  # contain float
        ]

        # invalid vaccine name
        self.invalid_vaccine_name = [
            self.create_citizen_reservation_info(vaccine_name="123"),   # contain integer
            self.create_citizen_reservation_info(vaccine_name="Taksin"),  # not the available vaccines
        ]

    def create_citizen_info(
            self,
            citizen_id="1102543765123",
            firstname="Peerasu",
            lastname="Watanasirang",
            birthdate="10 Oct 2000",
            occupation="Student",
            phone_number="0865194261",
            is_risk="false",
            address="66/6 Moodaeng rd. 10220"):
        """Return new dict of the registration API requested attributes.

        Args:
            citizen_id (str, optional): Identity Number for the citizen of Thailand, default is "1102543765123"
            firstname (str, optional): Firstname of the citizen, default is "Peerasu"
            lastname (str, optional): Lastname of the citizen, default is "Watanasirang"
            birthdate (str, optional): Birthdate of the citizen, default is "10 Oct 2000"
            occupation (str, optional): Occupation of the citizen, default is "Student"
            phone_number (str, optional): Phone number of the citizen, default is "0865194261"
            is_risk (str, optional): 7 COVID risks medical conditions status of the citizen, default is "false"
            address (str, optional): Address of the citizen, default is "66/6 Moodaeng rd. 10220"

        Returns:
            Dict: info of the registration API
        """
        return {
            'citizen_id': citizen_id,
            'name': firstname,
            'surname': lastname,
            'birth_date': birthdate,
            'occupation': occupation,
            'phone_number': phone_number,
            'is_risk': is_risk,
            'address': address
        }

    def create_citizen_reservation_info(self,
                                        citizen_id="1102543765123",
                                        site_name="Chakkrapan",
                                        vaccine_name="Astra"):
        """Return new dict of the reservation API requested attributes.

        Args:
            citizen_id (str, optional): Identity Number of the reservation, default to be "1102543765123"
            site_name (str, optional): Site name of the reservation, default to be "Chakkrapan"
            vaccine_name (str, optional): Vaccine name of the reservation, default to be "Astrazeneca"

        Returns:
            Dict: info of the reservation API
        """

        return {
            'citizen_id': citizen_id,
            'site_name': site_name,
            'vaccine_name': vaccine_name
        }

    def received_feedback(self, response):
        """Return a feedback of the response

        Args:
            response (Response): response returned from a requested URL

        Returns:
            str: feedback
        """
        return response.json()['feedback']

    def test_reserve_a_citizen(self):
        """Test reserving a citizen with all valid attributes
        """
        # send request
        response_registration = requests.post(registration_URL, data=self.citizen_registration)
        response = requests.post(reservation_URL, data=self.citizen_reservation)
        # check the status code
        self.assertEqual(response.status_code, 201)  # 201 means ok!
        # check feedback
        self.assertEqual(self.received_feedback(response_registration), FEEDBACK['success_registration'])
        self.assertEqual(self.received_feedback(response), FEEDBACK['success_reservation'])

    def test_reserve_with_missing_attribute(self):
        """Test reserving a citizen with some missing attribute
        """
        for info in self.missing_attribute:
            # send request
            response = requests.post(reservation_URL, data=info)
            # check feedback
            self.assertEqual(self.received_feedback(response), FEEDBACK['missing_attribute'])

    def test_already_reserved(self):
        """Test reserving the same citizen twice
        """
        # send requests
        response_registration = requests.post(registration_URL, data=self.citizen_registration)
        response1 = requests.post(reservation_URL, data=self.citizen_reservation)
        response2 = requests.post(reservation_URL, data=self.citizen_reservation)
        # check feedback
        self.assertEqual(self.received_feedback(response_registration), FEEDBACK['success_registration'])
        self.assertEqual(self.received_feedback(response1), FEEDBACK['success_reservation'])
        self.assertEqual(self.received_feedback(response2), FEEDBACK['reserved'])

    def test_reserve_without_registered(self):
        """Test reserving a citizen without registered
        """
        # send requests
        response = requests.post(reservation_URL, data=self.citizen_reservation)
        # check feedback
        self.assertEqual(self.received_feedback(response), FEEDBACK['not_registered'])

    def test_register_invalid_citizen_id(self):
        """Test register a person with invalid citizen_id
        """
        for info in self.invalid_citizen_id:
            # send request
            response = requests.post(reservation_URL, data=info)
            # check feedback
            self.assertEqual(self.received_feedback(response), FEEDBACK['invalid_citizen_id'])

    def test_reserve_with_invalid_vaccine_name(self):
        """Test reserving a citizen with the invalid vaccine name
        """
        # send request
        response_registration = requests.post(registration_URL, data=self.citizen_registration)
        # check feedback
        self.assertEqual(self.received_feedback(response_registration), FEEDBACK['success_registration'])
        for vaccine in self.invalid_vaccine_name:
            # send request
            response = requests.post(reservation_URL, data=vaccine)
            # check feedback
            self.assertEqual(self.received_feedback(response), FEEDBACK['invalid_vaccine_name'])


if __name__ == '__main__':
    unittest.main()
