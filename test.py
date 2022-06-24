import unittest

from text2system import user as user_lib
from text2system.aiengine import Intent
from text2system.config import ATTRIBUTE_OK, BYE, CANCEL, GREETINGS, HELP, SAVE_SUCCESS

class TestT2S(unittest.TestCase):
    #initializing some variables
    @classmethod
    def setUpClass(cls):
        cls.USER = user_lib.User.getRandomNewUser()
        cls.MUP = cls.USER.MUP
        cls.SE = cls.MUP.getSE()
        cls.AC = cls.SE.getAC()
        #simulating a user connection
        cls.user_data = {}
        cls.user_data['chat_id'] = '12345'
        cls.user_data['debug_mode'] = False
        
    def __assertInDefaultResponseList(self, msg, response_list):
        self.assertTrue(self.__talk(msg)['response_msg'] in response_list)

    def __talk(self, msg):
        return self.AC.app_chatbot_msgProcess(msg, self.user_data)

    def __check(self, cmd_str, intent, entity_name, attList, response_list=None):
        response = self.__talk(cmd_str)
        self.assertEqual(response['intent'], intent, 'intent not correct. response[intent]=' + str(response['intent']))
        self.assertEqual(response['entity_class_name'], entity_name, 'entity class not correct.\nresponse[entity_class_name]=' + 
                            str(response['entity_class_name']) + '\nentity_name=' + str(entity_name))
        att_dict = {}
        for i in range(0, len(attList), 2):
            att_dict[attList[i]] = attList[i+1]
            
        if intent != Intent.CONFIRMATION:
            self.assertEqual(response['attributes'], att_dict, 'attributes not correct.\nresponse[attributes]=' +
                        str(response['attributes']) + '\natt_list=' + str(attList))
        if response_list:    
            self.assertTrue(response['response_msg'] in response_list, 'response message not correct.\nresponse[response_msg]=' +
                            str(response['response_msg']) + '\nresponse_list=' + str(response_list))
    
    def __test_SAVE(self, entity_name, attList, cmd_str=None):
        if not cmd_str:
            cmd_str = 'add ' + entity_name
            if len(attList) > 0:
                cmd_str += ' with'
            for i in range(0, len(attList), 2):
                cmd_str += ' ' + attList[i]
                cmd_str += '=' + attList[i+1] + ","
        
        #TODO: lower case bug
        attList = [x.lower() for x in attList]
        cmd_str = cmd_str.lower()
        
        self.__check(cmd_str, Intent.SAVE, entity_name , attList, ATTRIBUTE_OK(str(Intent.SAVE), entity_name))
        self.__check('ok', Intent.CONFIRMATION, entity_name , attList, SAVE_SUCCESS)
            
    #testing the creation of the arquitecture elements
    def test_arquitecture_elements(self):
        self.assertIsNotNone(self.USER)
        self.assertIsNotNone(self.MUP) 
        self.assertIsNotNone(self.SE) 
        self.assertIsNotNone(self.AC)
    
    #testing the 'hi' msg
    def test_greetings(self):
        self.__assertInDefaultResponseList('hi', GREETINGS)
        
    #testing the 'bye' msg
    def test_bye(self):
        self.__assertInDefaultResponseList('bye', BYE)
        
    #testing the 'add' intent
    def test_add_intent(self):
        self.__test_SAVE('student', ['name', 'Anderson Martins Gomes', 'age', '20'])
        self.__test_SAVE('subject', ['name', 'Brazilian History', 'description', 'The history of Brazil'])
        self.__test_SAVE('teacher', ['name', 'Paulo Henrique', 'age', '65', 'email', 'ph@uece.br'])
        #save a subject name=Math, and description is 'The best subject ever!'
        self.__test_SAVE('subject', ['name', 'Math', 'description', "The best subject ever"])
        #TODO: solve the "'" problem
        #self.__test_SAVE('subject', ['name', 'Math', 'description', "The best subject ever!"], 
        #                 cmd_str="add subject with name=Math, description='The best subject ever!'")
    
    def test_cancel_intent(self):
        self.__check("add student name=Anderson", Intent.SAVE, "student" , ['name', 'Anderson'], ATTRIBUTE_OK(str(Intent.SAVE), "student"))
        self.__check('cancel', Intent.CANCEL, None , [], CANCEL)
        
    def test_help_intent(self):
        self.__check("help", Intent.HELP, None , [], HELP)
    
    def test_delete_intent(self):
        self.__check("delete student name is Anderson", Intent.DELETE, "student" , ['name', 'Anderson'], ATTRIBUTE_OK(str(Intent.DELETE), "student"))
        self.__check('ok', Intent.CONFIRMATION, "student", ['name', 'Anderson'])

    def test_read_intent(self):
        #TODO: fix the bug regards the intent type
        self.__check("show all students", Intent.CONFIRMATION, "student", []) 

if __name__ == '__main__':
    unittest.main()