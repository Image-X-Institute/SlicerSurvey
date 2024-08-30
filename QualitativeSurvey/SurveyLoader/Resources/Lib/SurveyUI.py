import slicer, qt
from abc import ABCMeta, abstractmethod


class QuestinoWidgetMeta(ABCMeta, type(qt.QWidget)):
    pass


class QuestionWidget(qt.QWidget, metaclass=QuestinoWidgetMeta):
    def __init__(self, num:int, question:str, images:list, choices:list) -> None:
        super().__init__(self)
        self.num = num
        self.question = question
        self.question_display = None
        self.images = images
        self.choices = choices
        self.answers = []
        self.main_layout = None

        self.setMinimumWidth(400)

    @abstractmethod
    def _formatSelfLayout(self) -> bool:
        pass

    @abstractmethod
    def getAnswers(self) -> list:
        pass

    def getNumber(self) -> int:
        return self.num
    
    def getQuestion(self) -> str:
        return self.question
    
    def getChoices(self) -> list:
        return self.choices
    
    def getImages(self) -> list:
        return self.images
    
    def setImages(self, images:list) -> bool:
        self.images = images
        return True
    
    @abstractmethod
    def setAnswer(self) -> bool:
        pass
    
    @abstractmethod
    def setChoices(self, choices:list) -> bool:
        pass

    def setNumber(self, num:int) -> bool:
        self.num = num
        return True

    def setQuestion(self, question:str) -> bool:
        self.question = question
        self.question_display.setText(question)
        return True

    def toCSV(self) -> str:
        formatted_question = "'" + self.question.strip()
        csv_string = '"{}",'.format(formatted_question)

        for answer in self.getAnswers():
            if answer == '' or answer is None:
                    csv_string += '"Question Unanswered",'
            else:
                formatted_answer = "'" + answer.strip()
                csv_string += '"{}",'.format(formatted_answer)
        return csv_string[:-1]+"\n" if csv_string[-1] == "," else csv_string+"\n"

    def _checkQuestionCSVFormat(self, question:str) -> bool:
        if len(question) < 2:
            print(f"Question {self.num} cannot be loaded: Wrong question CSV format")
        elif question[0] != "'":
            print(f"Question {self.num} cannot be loaded: Wrong question CSV format")
        elif question[1:] != self.question:
            print(f"Question {self.num} cannot be loaded: Question unmatched")
        else:
            return True
        
    def _checkAnswerCSVFormat(self, answer:str) -> str:
        if len(answer) < 2:
            print(f"Question {self.num} cannot be loaded: Wrong answer CSV format")
        elif answer == "Question Unanswered":
            return ""
        elif answer[0] != "'":
            print(f"Question {self.num} cannot be loaded: Wrong answer CSV format")
        else:
            return answer[1:]

    @abstractmethod
    def fromCSV(self, data:list) -> bool:
        pass

    
class MultiSingleQuestion(QuestionWidget):
    def __init__(self, num:int, question:str, images:list, choices:list) -> None:
        super().__init__(num, question, images, choices)
        self._formatSelfLayout()

    def _formatSelfLayout(self) -> bool:
        self.main_layout = qt.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(qt.QLabel("Question {}.".format(self.num)))

        self.question_display = qt.QLabel(self.question)
        self.question_display.setWordWrap(True)
        self.main_layout.addWidget(self.question_display)
        self.button_group = qt.QButtonGroup()
        
        for choice in self.choices:
            radio_button = qt.QRadioButton(choice)
            self.button_group.addButton(radio_button)
            self.main_layout.addWidget(radio_button)

        return True

    def getAnswers(self) -> list:
        checked = self.button_group.checkedButton()
        return [checked.text] if checked is not None else [None]
    
    def setAnswer(self, answer:str) -> bool:
        if answer not in self.choices:
            return False
        elif answer == self.getAnswers()[0]:
            return True
        else:
            for button in self.button_group.buttons():
                if button.text == answer:
                    button.setChecked(True)
            return True
    
    def setChoices(self, choices:list) -> bool:
        buttons = self.button_group.buttons()
        if len(choices) != len(buttons):
            return False
        else:
            for i in range(len(buttons)):
                buttons[i].setText(choices[i])
        
        return True
    
    def fromCSV(self, data:list) -> bool:
        if len(data) != 2:
            return False
        
        question = self._checkQuestionCSVFormat(data[0])
        if not question:
            return False
        
        answer = self._checkAnswerCSVFormat(data[1])
        if answer is None:
            return False
        elif answer == "":
            return True
        elif not self.setAnswer(answer):
            print(f"Question {self.num} cannot be loaded: Answer unmatched")
            return False
        return True


class MultiMultiQuestion(QuestionWidget):
    def __init__(self, num:int, question:str, images:list, choices:list) -> None:
        super().__init__(num, question, images, choices)
        self._formatSelfLayout()

    def _formatSelfLayout(self) -> bool:
        self.main_layout = qt.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(qt.QLabel("Question {}.".format(self.num)))
        
        self.question_display = qt.QLabel(self.question)
        self.main_layout.addWidget(self.question_display)
        self.button_group = qt.QButtonGroup()

        count = 0
        for choice in self.choices:
            checkbox = qt.QCheckBox(choice)
            self.button_group.addButton(checkbox)
            self.button_group.setId(checkbox, count)
            self.main_layout.addWidget(checkbox)
            count += 1

        self.button_group.setExclusive(False)
        return True

    def getAnswers(self) -> list:
        answers = []
        for button in self.button_group.buttons():
            if button.isChecked():
                answers.append(button.text)

        return answers if len(answers) != 0 else [None]
    
    def setAnswer(self, answers:list) -> bool:
        if len(answers) > len(self.choices):
            return False
        
        indices = []
        for answer in answers:
            if answer not in self.choices:
                return False
            else:
                indices.append(self.choices.index(answer))
        
        for button in self.button_group.buttons():
            button.setChecked(self.button_group.id(button) in indices)
        return True
    
    def setChoices(self, choices:list) -> bool:
        buttons = self.button_group.buttons()
        if len(choices) != len(buttons):
            return False
        else:
            for i in range(len(buttons)):
                buttons[i].setText(choices[i])
        
        return True
    
    def fromCSV(self, data:list) -> bool:
        if len(data) < 2:
            return False
        
        question = self._checkQuestionCSVFormat(data[0])
        if not question:
            return False
        
        answers = []
        for each in data[1:]:
            answer = self._checkAnswerCSVFormat(each)
            if answer is None:
                return False
            elif answer == "":
                return True
            elif answer not in self.choices:
                print(f"Question {self.num} cannot be loaded: Answer unmatched")
                return False
            else:
                answers.append(answer)

        return self.setAnswer(answers)


class OpenEndedQuestion(QuestionWidget):
    def __init__(self, num:int, question:str, images:list) -> None:
        super().__init__(num, question, images, [])
        self._formatSelfLayout()

    def _formatSelfLayout(self) -> bool:
        self.main_layout = qt.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(qt.QLabel("Question {}.".format(self.num)))
        
        self.question_display = qt.QLabel(self.question)
        self.main_layout.addWidget(self.question_display)

        self.answer_box = qt.QTextEdit()
        self.main_layout.addWidget(self.answer_box)
        
        return True

    def getAnswers(self) -> list:
        return [self.answer_box.toPlainText()]

    def setAnswer(self, answer:str) -> bool:
        self.answer_box.setText(answer)
        return True

    def setChoices(self):
        pass
    
    def fromCSV(self, data:list) -> bool:
        if len(data) != 2:
            return False
        
        question = self._checkQuestionCSVFormat(data[0])
        if not question:
            return False
        
        answer = self._checkAnswerCSVFormat(data[1])
        if answer is None:
            return False
        else:
            return self.setAnswer(answer)


class DropDownQuestion(QuestionWidget):
    def __init__(self, num:int, question:str, images:list, choices:list) -> None:
        choices.insert(0, "Question Unanswered")
        super().__init__(num, question, images, choices)
        self._formatSelfLayout()

    def _formatSelfLayout(self) -> bool:
        self.main_layout = qt.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(qt.QLabel("Question {}.".format(self.num)))
        
        self.question_display = qt.QLabel(self.question)
        self.main_layout.addWidget(self.question_display)

        self.combo_box = qt.QComboBox()

        for choice in self.choices:
            self.combo_box.addItem(choice)

    
        self.main_layout.addWidget(self.combo_box)
        return True
    
    def getAnswers(self) -> list:
        answer = self.combo_box.currentText
        return [answer] if answer != "Question Unanswered" else [None]
    
    def setAnswer(self, answer:str) -> bool:
        if answer not in self.choices:
            return False
        self.combo_box.currentText = answer
        return True

    def setChoices(self, choices:list) -> bool:
        if len(choices) != self.combo_box.count:
            return False
        else:
            for i in range(len(choices)):
                self.combo_box.setItemText(i, choices[i])
        
        return True
    
    def fromCSV(self, data:list) -> bool:
        if len(data) != 2:
            return False
        
        question = self._checkQuestionCSVFormat(data[0])
        if not question:
            return False
        
        answer = self._checkAnswerCSVFormat(data[1])
        if answer is None:
            return False
        elif answer == "":
            self.setAnswer("Question Unanswered")
            return True
        elif not self.setAnswer(answer):
            print(f"Question {self.num} cannot be loaded: Answer unmatched")
            return False
        return True


class SliderQuestion(QuestionWidget):
    def __init__(self, num:int, question: str, images:list, left_bound:int, right_bound:int) -> None:
        super().__init__(num, question, images, [left_bound, right_bound])
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.slid = False
        self._formatSelfLayout()

    def _change_display(self) -> None:
        self.slider_display.setText(self.slider.value)
        self.slid = True

    def _formatSelfLayout(self) -> bool:
        self.main_layout = qt.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addWidget(qt.QLabel("Question {}.".format(self.num)))

        self.question_display = qt.QLabel(self.question)
        self.main_layout.addWidget(self.question_display)

        slider_widget = qt.QWidget()
        slider_layout = qt.QHBoxLayout()
        slider_widget.setLayout(slider_layout)

        self.slider = qt.QSlider(qt.Qt.Horizontal)
        self.slider_display = qt.QLabel(self.left_bound)

        self.slider.setMinimum(self.left_bound)
        self.slider.setMaximum(self.right_bound)
        self.slider.value = self.left_bound
        self.slider.setTracking(True)
        self.slider.setSingleStep(1)
        self.slider.valueChanged.connect(self._change_display)

        slider_layout.addWidget(self.slider)
        slider_layout.addWidget(self.slider_display)
        self.main_layout.addWidget(slider_widget)
        return True
    
    def getAnswers(self) -> list:
        if not self.slid:
            return [None]
        return [str(self.slider.value)]
    
    def setAnswer(self, answer:int) -> bool:
        if not (self.choices[0] <= answer <= self.choices[1]):
            return False
        self.slider.value = answer
        return True


    def getSliderRange(self) -> list:
        return self.choices
    
    def setLeftBound(self, left_bound:int) -> bool:
        self.left_bound = left_bound
        self.slider.setMinimum(left_bound)
        self.choices[0] = left_bound
        return True
    
    def setRightBound(self, right_bound:int) -> bool:
        self.right_bound = right_bound
        self.slider.setMaximum(right_bound)
        self.choices[1] = right_bound
        return True
    
    def setChoices(self, choices: list) -> bool:
        if len(choices) == 2:
            self.setLeftBound(choices[0])
            self.setRightBound(choices[1])

    def fromCSV(self, data:list) -> bool:
        if len(data) != 2:
            return False
        
        question = self._checkQuestionCSVFormat(data[0])
        if not question:
            return False
        
        answer = self._checkAnswerCSVFormat(data[1])
        if answer is None:
            return False
        elif answer == "":
            self.slid = False
            return True
        elif not self.setAnswer(int(answer)):
            print(f"Question {self.num} cannot be loaded: Answer unmatched")
            return False
        self.slid = True
        return True
            

class RatingScaleQuestion(QuestionWidget):
    def __init__(self, num:int, question:str, images:list, left_bound:int, right_bound:int, step:int) -> None:
        super().__init__(num, question, images, [left_bound, right_bound, step])
        self.left_bound = left_bound
        self.right_bound = right_bound
        self.step = step
        self._formatSelfLayout(True)

    def _buttonSelected(self) -> None:
        pass

    def _formatSelfLayout(self, initial:bool) -> bool:
        if initial:
            self.main_layout = qt.QVBoxLayout()
            self.setLayout(self.main_layout)
            self.main_layout.addWidget(qt.QLabel("Question {}.".format(self.num)))
            self.question_display = qt.QLabel(self.question)
            self.main_layout.addWidget(self.question_display)
        else:
            self.rating_widget.setParent(None)

        self.rating_widget = qt.QWidget()
        self.rating_layout = qt.QHBoxLayout()
        self.rating_layout.setSpacing(0)
        self.rating_widget.setLayout(self.rating_layout)
        self.button_group = qt.QButtonGroup()

        for i in range(self.left_bound, self.right_bound + 1, self.step):
            button = qt.QPushButton(str(i))
            button.setCheckable(True)
            self.button_group.addButton(button)
            self.rating_layout.addWidget(button)

        self.button_group.setExclusive(True)
        self.button_group.buttonToggled.connect(self._buttonSelected)
        self.main_layout.addWidget(self.rating_widget)
        return True
    
    def getAnswers(self) -> list:
        checked = self.button_group.checkedButton()
        return [checked.text] if checked is not None else [None]
    
    def setAnswer(self, answer:int) -> bool:
        if not (self.choices[0] <= answer <= self.choices[1]):
            return False
        for button in self.button_group.buttons():
            if int(button.text) == answer:
                button.setChecked(True)
                return True
        return False

    def getRatingRange(self) -> list:
        return self.choices[:2]
    
    def getRatingStep(self) -> int:
        return self.choices[2]
    
    def setLeftBound(self, left_bound:int) -> bool:
        self.left_bound = left_bound
        self.choices[0] = left_bound
        self._formatSelfLayout(False)
        return True
    
    def setRightBound(self, right_bound:int) -> bool:
        self.right_bound = right_bound
        self.choices[1] = right_bound
        self._formatSelfLayout(False)
        return True
    
    def setStep(self, step:int) -> bool:
        self.step = step
        self.choices[2] = step
        self._formatSelfLayout(False)
        return True
    
    def setChoices(self, choices: list) -> bool:
        if len(choices) == 3:
            self.setLeftBound(choices[0])
            self.setRightBound(choices[1])
            self.setStep(choices[2])

    def fromCSV(self, data:list) -> bool:
        if len(data) != 2:
            return False
        
        question = self._checkQuestionCSVFormat(data[0])
        if not question:
            return False
        
        answer = self._checkAnswerCSVFormat(data[1])
        if answer is None:
            return False
        elif answer == "":
            return True
        elif not self.setAnswer(int(answer)):
            print(f"Question {self.num} cannot be loaded: Answer unmatched")
            return False
        return True