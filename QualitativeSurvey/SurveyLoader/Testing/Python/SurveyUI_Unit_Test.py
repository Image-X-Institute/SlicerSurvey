from Resources.Lib.SurveyUI import *
import sys
import os

# Get the path to the grandparent directory (two levels up from your_script.py)
grandparent_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', '..', '..'))

# Add the grandparent directory to the sys.path
sys.path.append(grandparent_dir)



class Test_SurveyUI():
    def __init__(self, slicer):
        self.slicer = slicer

    def test_MultiSingleQuestion(self):
        choices = ["c1", "c2", "c3"]
        label = "question 1"
        multi_single_q = MultiSingleQuestion(1, label, [], choices)

        # Test the question is initialize correctly
        self.slicer.assertTrue(multi_single_q.num, 1)
        self.slicer.assertTrue(multi_single_q.question, label)
        self.slicer.assertTrue(multi_single_q.choices, choices)

        # Test the question return None when no answer is selected
        self.slicer.assertEqual(multi_single_q.getAnswers(), [None])

        new_choices = ["c1"]
        # Test the question cannot reset the choices when new choices are in different amount
        self.slicer.assertFalse(multi_single_q.setChoices(new_choices))

        new_choices = ["c1", "c2", "c3"]
        # Test the question can reset the choices when new choices are in the same amount
        self.slicer.assertTrue(multi_single_q.setChoices(new_choices))

        # Test the question can reset the question label
        self.slicer.assertTrue(multi_single_q.setQuestion("new question"))

        # Test the get image correctly
        self.slicer.assertEqual(multi_single_q.getImages(), [])

        # Test the set image correctly
        self.slicer.assertTrue(multi_single_q.setImages([]))

        # Test to csv file correctly
        buttons = multi_single_q.button_group.buttons()
        buttons[0].setChecked(True)
        self.slicer.assertEqual(multi_single_q.toCSV(), '@new question,@c1\n')

    def test_MultiMultiQuestion(self):
        choices = ["c1", "c2", "c3"]
        label = "question 1"
        multi_multi_q = MultiMultiQuestion(1, label, [], choices)

        # Test the question is initialize correctly
        self.slicer.assertTrue(multi_multi_q.num, 1)
        self.slicer.assertTrue(multi_multi_q.question, label)
        self.slicer.assertTrue(multi_multi_q.choices, choices)

        # Test the question return None when no answer is selected
        self.slicer.assertEqual(multi_multi_q.getAnswers(), [None])

        new_choices = ["c1"]
        # Test the question cannot reset the choices when new choices are in different amount
        self.slicer.assertFalse(multi_multi_q.setChoices(new_choices))

        new_choices = ["c1", "c2", "c3"]
        # Test the question can reset the choices when new choices are in the same amount
        self.slicer.assertTrue(multi_multi_q.setChoices(new_choices))

        # Test the question can reset the question label
        self.slicer.assertTrue(multi_multi_q.setQuestion("new question"))

        # Test the get image correctly
        self.slicer.assertEqual(multi_multi_q.getImages(), [])

        # Test the set image correctly
        self.slicer.assertTrue(multi_multi_q.setImages([]))

        # Test to csv file correctly
        buttons = multi_multi_q.button_group.buttons()
        buttons[0].setChecked(True)
        buttons[1].setChecked(True)
        self.slicer.assertEqual(multi_multi_q.toCSV(), '@new question,@c1,@c2\n')

    def test_RatingScaleQuestion(self):
        # Test the question is initialize correctly
        question = RatingScaleQuestion(1, "question 1", [], 1, 5, 1)
        self.slicer.assertEqual(question.getNumber(), 1)
        self.slicer.assertEqual(question.getQuestion(), "question 1")
        self.slicer.assertEqual(question.getRatingRange(), [1, 5])
        self.slicer.assertEqual(question.getRatingStep(), 1)
        self.slicer.assertEqual(question.getAnswers(), [None])
        self.slicer.assertEqual(question.getChoices(), [1, 5, 1])

        # Test the question set values correctly
        question.setLeftBound(0)
        question.setRightBound(10)
        question.setStep(2)
        self.slicer.assertEqual(question.getRatingRange(), [0, 10])
        self.slicer.assertEqual(question.getRatingStep(), 2)

        question.setQuestion("new question")
        self.slicer.assertEqual(question.getQuestion(), "new question")

        # Test the question return None when no answer is selected
        self.slicer.assertEqual(question.getAnswers(), [None])

        new_choices = [1, 2, 3]
        # Test the question can reset the choices when new choices are in the same amount
        self.slicer.assertEqual(question.setChoices(new_choices), None)

        # Test the get image correctly
        self.slicer.assertEqual(question.getImages(), [])

        # Test the set image correctly
        self.slicer.assertTrue(question.setImages([]))

        # Test to csv file correctly
        buttons = question.button_group.buttons()
        buttons[0].setChecked(True)
        self.slicer.assertEqual(question.toCSV(), '@new question,@1\n')

    def test_OpenEndedQuestion(self):
        question_number = 6
        question_name = "question 6"
        open_ended_question = OpenEndedQuestion(question_number, question_name, [])

        #Test question intialisation 
        self.slicer.assertEqual(open_ended_question.num, question_number)
        self.slicer.assertEqual(open_ended_question.question, question_name)
        self.slicer.assertEqual(open_ended_question.images, [])

        #Test empty
        self.slicer.assertEqual(open_ended_question.getAnswers(), [''])

        #Test answered
        open_ended_question.answer_box.setPlainText("test answer")
        self.slicer.assertEqual(open_ended_question.getAnswers(), ["test answer"])
       
        #Test change question name       
        open_ended_question.setQuestion("new question test")
        self.slicer.assertEqual(open_ended_question.getQuestion(), "new question test")
        
        #Test get images
        self.slicer.assertEqual(open_ended_question.getImages(), [])

        #Test set images
        self.slicer.assertTrue(open_ended_question.setImages([]))

        #Test to csv 
        self.slicer.assertEqual(open_ended_question.toCSV(), "@new question test,@test answer\n")
    
    def test_DropDownQuestion(self):
        question_number = 2
        question_name = "Question 2"
        choices = ["2", "1", "3", "4"]
        drop_down_question = DropDownQuestion(question_number, question_name, [], choices)

        #Test intialisation
        self.slicer.assertEqual(drop_down_question.num, question_number)
        self.slicer.assertEqual(drop_down_question.question, question_name)
        self.slicer.assertEqual(drop_down_question.images, [])
        self.slicer.assertEqual(drop_down_question.choices, choices)
        self.slicer.assertEqual(drop_down_question.getAnswers(), ["Default"])

        #Test answered
        drop_down_question.combo_box.setCurrentText("5")
        self.slicer.assertEqual(drop_down_question.getAnswers(), ["Default"])
        drop_down_question.combo_box.setCurrentText("4")
        self.slicer.assertEqual(drop_down_question.getAnswers(), ["4"])

        #Test setChoices
        new_choices = ["1", "2"]
        self.slicer.assertFalse(drop_down_question.setChoices(new_choices))     
        # I think the addition of the Default choice has broken this test  
        print(drop_down_question.getChoices())
        new_choices_2 = ["Default", "1", "2", "3", "4"]
        self.slicer.assertTrue(drop_down_question.setChoices(new_choices_2))    

        #Test change question name       
        drop_down_question.setQuestion("new question test")
        self.slicer.assertEqual(drop_down_question.getQuestion(), "new question test")

        #Test get images
        self.slicer.assertEqual(drop_down_question.getImages(), [])

        #Test set images
        self.slicer.assertTrue(drop_down_question.setImages([]))

        #Test to csv 
        self.slicer.assertEqual(drop_down_question.toCSV(), "@new question test,@4\n")
    
    def test_SliderQuestion(self):
        question_number = 3
        question_name = "Question 3"
        choices = [1, 5]
        slider_question = SliderQuestion(question_number, question_name, [], choices[0], choices[1])

        #Test initialisation
        self.slicer.assertEqual(slider_question.num, question_number)
        self.slicer.assertEqual(slider_question.question, question_name)
        self.slicer.assertEqual(slider_question.images, [])
        self.slicer.assertEqual(slider_question.left_bound, choices[0])
        self.slicer.assertEqual(slider_question.right_bound, choices[1])

        #Test slider answer
        slider_question.slided = True
        self.slicer.assertEqual(slider_question.getAnswers(), [1])
        slider_question.slider.setValue(3)
        self.slicer.assertEqual(slider_question.getAnswers(), [3])

        #Test slider range
        self.slicer.assertEqual(slider_question.getSliderRange(), choices)

        #test bounds
        slider_question.setLeftBound(0)
        self.slicer.assertEqual(slider_question.left_bound, 0)
        slider_question.setRightBound(6)
        self.slicer.assertEqual(slider_question.right_bound, 6)


        #Test change question name       
        slider_question.setQuestion("new question test")
        self.slicer.assertEqual(slider_question.getQuestion(), "new question test")
        
        #Test get images
        self.slicer.assertEqual(slider_question.getImages(), [])

        #Test set images
        self.slicer.assertTrue(slider_question.setImages([]))

        #Test set choices
        slider_question.setChoices([0, 4])
        self.slicer.assertEqual(slider_question.left_bound, 0)
        self.slicer.assertEqual(slider_question.right_bound, 4)
        
        #Test to csv 
        self.slicer.assertEqual(slider_question.toCSV(), "@new question test,@3\n")
    