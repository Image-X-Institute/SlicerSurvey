import csv, ast
import Resources.Lib.SurveyUI as SurveyUI
import qt, slicer
from pathlib import Path, PurePath


class SurveyItem: 
    def __init__(self, text, type, images, choices):
        self.text = text
        self.type = type
        self.images = ast.literal_eval(images)
        self.choices = ast.literal_eval(choices)


#
# SurveyQuestionnaire
#
class SurveyQuestionnaire:
    def __init__(self, csv_path:str, questions_container:qt.QLayout, navigations_container:qt.QLayout, footer_container:qt.QLayout):
        self.csv_path = csv_path
        self.questions_container = questions_container
        self.navigations_container = navigations_container
        self.footer_container = footer_container
        self.question_widgets = []
        self.loaded_image_nodes = []
        self.current_num = 0
        self.current_question = None
        self.questions_dropdown = None
        self.finish_button = None
        self.resume_button = None

        self._loadSurveyData()
        self._generateQuestions()
        
        self._formatQuestions()
        self._formatNavigations()
        self._formatFooter()

    def close(self):
        self._clearQuestions()
        self._clearNavigations()
        self._clearData()
        self._clearFooter()

    def _loadSurveyData(self):
        try:
            print(f"Loading data from {self.csv_path}...")
            with open(self.csv_path, newline='') as csvFile:
                reader = csv.reader(csvFile)
                next(reader)
                self.questions_items = [SurveyItem(*row) for row in reader]
        except:
            self._invalidCSV("Invalid CSV")
        finally:
            if(not self.questions_items):
                self._invalidCSV("Invalid CSV")

    def _clearNavigations(self):
        child = self.navigations_container.takeAt(0)
        while child:
            del(child)
            child = self.navigations_container.takeAt(0)

    def _clearQuestions(self):
        for i in range(self.questions_container.count()):
            item = self.questions_container.itemAt(i)

            if item:
                widget = self.questions_container.itemAt(i).widget()
                widget.setParent(None)
                del(widget)

    def _clearData(self):
         if slicer.mrmlScene:
            for node in self.loaded_image_nodes:
                slicer.mrmlScene.RemoveNode(node)
            self.loaded_image_nodes = []

    def _clearFooter(self):
        if self.finish_button:
            self.finish_button.setParent(None)
        if self.resume_button:
            self.resume_button.setParent(None)

    def _loadQuestionImage(self):
        try:
            self._clearData()
            for each in self.current_question.getImages():
                node = self.loadNode(each)
                node.SetName(each)
                self.loaded_image_nodes.append(node)
            if (len(self.loaded_image_nodes) >= 2):
                slicer.util.setSliceViewerLayers(
                    background=self.loaded_image_nodes[0],
                    foreground=self.loaded_image_nodes[1]
                )
        except:
            _invalid_csv("An Image Could Not Be Loaded")

    def loadNode(self, nodeName):
        questionnaire_dir = PurePath(self.csv_path).parents[0]
        path = PurePath(questionnaire_dir, f"{nodeName}")
        if (not Path(path).exists()):
            raise FileNotFoundError(f"File {path} does not exist")
        
        filetype = slicer.app.coreIOManager().fileType(path)
        node = slicer.util.loadNodeFromFile(path, filetype)
        return node

    @staticmethod
    def createQuestionWidget(num:int, question:SurveyItem):
        type = question.type
        text = question.text
        choices = question.choices
        images = question.images

        if type == 'multi_multi':
            return SurveyUI.MultiMultiQuestion(num, text, images, choices)
        elif type == 'multi_single':
            return SurveyUI.MultiSingleQuestion(num, text, images, choices)
        elif type == 'open':
            return SurveyUI.OpenEndedQuestion(num, text, images)
        elif type == 'dropdown':
            return SurveyUI.DropDownQuestion(num, text, images, choices)
        elif type == 'slider':
            return SurveyUI.SliderQuestion(num, text, images, choices[0], choices[1])
        elif type == 'rating':
            return SurveyUI.RatingScaleQuestion(num, text, images, choices[0], choices[1], choices[2])
        else:
            _invalid_csv("Invalid Question Type in CSV")
            raise Exception(f"UI Type {type} not supported")

    def _generateQuestions(self):
        for i in range(len(self.questions_items)):
            question = self.questions_items[i]
            new_question_widget = self.createQuestionWidget(i+1, question)
            self.question_widgets.append(new_question_widget)
        
        self.current_num = 0
        self.current_question = self.question_widgets[self.current_num]

    def _formatQuestions(self):
        self._clearQuestions()
        self.questions_container.insertWidget(self.questions_container.count() - 1, self.current_question)
        self._loadQuestionImage()

    def _formatNavigations(self):
        self._clearNavigations()

        self.to_first_button = qt.QPushButton("To First")
        self.prev_button = qt.QPushButton("Prev")
        self.next_button = qt.QPushButton("Next")
        self.to_last_button = qt.QPushButton("To Last")

        self.to_first_button.setEnabled(False)
        self.prev_button.setEnabled(False)

        questions_dropdown = qt.QComboBox()
        questions_dropdown.setMaximumWidth(45)
        for i in range(len(self.question_widgets)):
            questions_dropdown.addItem(str(i + 1))
        questions_dropdown.setCurrentIndex(self.current_num)
        questions_dropdown.currentIndexChanged.connect(self._toSelectedQuestion)
        self.questions_dropdown = questions_dropdown

        self.to_first_button.clicked.connect(self._toFirstQuestion)
        self.to_last_button.clicked.connect(self._toLastQuestion)
        self.prev_button.clicked.connect(self._toPrevQuestion)
        self.next_button.clicked.connect(self._toNextQuestion)

        buttons = [self.to_first_button, self.prev_button, questions_dropdown, self.next_button, self.to_last_button]
        for button in buttons:
            self.navigations_container.addWidget(button)
    
    def _formatFooter(self):
        self._clearFooter()
        finish_button = qt.QPushButton("Save Progress")
        finish_button.clicked.connect(self._saveSurveyProgress)
        self.finish_button = finish_button
        self.footer_container.addWidget(finish_button)

        resume_button = qt.QPushButton("Load Progress")
        resume_button.clicked.connect(self._resumeSurveyProgress)
        self.resume_button = resume_button
        self.footer_container.addWidget(resume_button)

    def toQuestion(self, num:int):
        self._checkCurrentQuestionUnanswered()
        self.current_num = num
        self.current_question = self.question_widgets[num]

        self._setNavigationButtonStatus()

        state = self.questions_dropdown.blockSignals(True)
        self.questions_dropdown.setCurrentIndex(num)
        self.questions_dropdown.blockSignals(state)
        self._formatQuestions()

    def _toSelectedQuestion(self):
        if self.questions_dropdown:
            self.toQuestion(self.questions_dropdown.currentIndex)

    def _toFirstQuestion(self):
        self.toQuestion(0)

    def _toLastQuestion(self):
        self.toQuestion(len(self.question_widgets) - 1)

    def _toPrevQuestion(self):
        self.toQuestion(self.current_num - 1)

    def _toNextQuestion(self):
        self.toQuestion(self.current_num + 1)

    def _saveSurveyProgress(self):
        abs_path = PurePath(Path(__file__).parent.parent.parent,"Results", f"defaultName")
        filename = qt.QFileDialog.getSaveFileName(None, "Save CSV File", abs_path, "CSV Files (*.csv)")

        if filename and filename.endswith(".csv"):
            with open(filename, mode='w') as csvFile:
                for idx, question in enumerate(self.question_widgets):
                    # If user chose to be anonymous, skip saving the name
                    if idx == 0 and self.question_widgets[1].getAnswers()[0] == "yes":
                        continue
                    csvFile.write(question.toCSV())

    def _resumeSurveyProgress(self):
        abs_path = PurePath(Path(__file__).parent.parent.parent,"Results", f"defaultName")
        filename = qt.QFileDialog.getOpenFileName(None, "Load CSV File", abs_path, "CSV Files (*.csv)")

        if filename and filename.endswith(".csv"):
            with open(filename, mode='r') as csv_file:
                csv_reader = csv.reader(csv_file)
                counter = 0
                for row in csv_reader:
                    current_question = self.question_widgets[counter]
                    counter+=1

                    if not current_question.fromCSV(row):
                        self._dialogUnmatched(counter)

    def _checkCurrentQuestionUnanswered(self):
        self.current_question = self.question_widgets[self.current_num]
        if isinstance(self.current_question, SurveyUI.SliderQuestion):
            # Check if the slider has been moved
            if self.current_question.slid is False:
                dialog = CustomDialog(self.current_num + 1)
                result = dialog.exec_()
                if result == 1:
                    self.current_question.slid = True
        elif self.current_question.getAnswers() == [None]:
            self._dialogUnanswered()
        elif isinstance(self.current_question, SurveyUI.DropDownQuestion):
            # Check if the value is default
            if self.current_question.getAnswers() == ['Question Unanswered']:
                self._dialogUnanswered()
        elif isinstance(self.current_question, SurveyUI.OpenEndedQuestion):
            # Check if the value is default
            if self.current_question.getAnswers() == ['']:
                self._dialogUnanswered()

    def _dialogUnanswered(self):
        # Create a pop-up dialog
        dialog = qt.QDialog()
        dialog.setWindowTitle("Question Not Answered")
        layout = qt.QVBoxLayout()
        label = qt.QLabel(f"Question {self.current_num + 1} is not answered")
        font = qt.QFont()
        font.setPointSize(14) 
        label.setFont(font)
        layout.addWidget(label)
        dialog.setLayout(layout)
        dialog.exec_()

    def _dialogUnmatched(self, num):
        # Create a pop-up dialog
        dialog = qt.QDialog()
        dialog.setWindowTitle("Answer Unmatched")
        
        layout = qt.QVBoxLayout()
        label = qt.QLabel(f"Answer {num} does not match to question {num}")
        font = qt.QFont()
        font.setPointSize(14) 
        label.setFont(font)
        layout.addWidget(label)
        dialog.setLayout(layout)
        dialog.exec_()

    def _setNavigationButtonStatus(self):
        if (self.current_num == 0):
            self.prev_button.setEnabled(False)
            self.to_first_button.setEnabled(False)
        else:
            self.prev_button.setEnabled(True)
            self.to_first_button.setEnabled(True)
        
        if (self.current_num == len(self.question_widgets) - 1):
            self.next_button.setEnabled(False)
            self.to_last_button.setEnabled(False)
        else:
            self.next_button.setEnabled(True)
            self.to_last_button.setEnabled(True)

    def _invalidCSV(msg):
        dialog = qt.QDialog()
        dialog.setWindowTitle("File Invalid")
        dialog.setSizePolicy(qt.QSizePolicy.Expanding, qt.QSizePolicy.Expanding)
        layout = qt.QVBoxLayout()
        label = qt.QLabel(msg)
        font = qt.QFont()
        font.setPointSize(14) 
        label.setFont(font)
        layout.addWidget(label)
        dialog.setLayout(layout)
        dialog.exec_()

class CustomDialog(qt.QDialog):
    def __init__(self, current_num, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Unanswered Slider Question")

        layout = qt.QVBoxLayout()
        self.setLayout(layout)

        label = qt.QLabel(f"Slider for Question {current_num} has not been moved, is the answer what you want?")
        font = qt.QFont()
        font.setPointSize(14) 
        label.setFont(font)
        layout.addWidget(label)

        yes_button = qt.QPushButton("Yes")
        no_button = qt.QPushButton("No")

        layout.addWidget(yes_button)
        layout.addWidget(no_button)

        yes_button.clicked.connect(self.yesClicked)
        no_button.clicked.connect(self.noClicked)

    def yesClicked(self):
        self.accept()

    def noClicked(self):
        self.reject()
