from flask import Flask, jsonify, request
from models import db, VoiceExcercises, VoiceExcercisesHistory, Module, Award
from datetime import datetime
import os
from dotenv import load_dotenv
from flask_cors import CORS, cross_origin
import speech_recognition as sr
from pydub import AudioSegment




from jiwer import wer

import logging

from difflib import SequenceMatcher
import json
import base64
from flask_migrate import Migrate
load_dotenv()
migrate = Migrate()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate.init_app(app, db) 

CORS(app, origins=[
    "http://localhost:3000", 
    "https://capstone-lms.vercel.app", 
    "https://capstone-b5lfpvbba-paragons-projects-6f921143.vercel.app"
])

@app.route('/', methods=['GET'])
def hello_world():
    return jsonify({"message": "Hello World!"}), 200

def assign_award(average_score):
    """Helper function to assign award based on average score"""
    if average_score >= 95:
        return "Star Badge"
    elif average_score >= 90:
        return "Gold Badge"
    elif average_score >= 80:
        return "Silver Badge"
    elif average_score >= 70:
        return "Bronze Badge"
    return None

def calculate_student_voice_awards(student_id):
    """Calculate student awards based on voice exercise history"""
  
    voice_history = VoiceExcercisesHistory.query.filter_by(studentId=student_id).all()

  
    if not voice_history:
        return jsonify({"message": "No voice exercise history found for this student."}), 200

   
    total_voice_score = sum([voice.score for voice in voice_history])
    average_voice_score = total_voice_score / len(voice_history) if voice_history else 0

 
    voice_award = assign_award(average_voice_score)

    
    if voice_award:
        new_award = Award(
            studentId=student_id,
            awardType=voice_award,
            tier="Voice Exercises",
            createdAt=datetime.now()
        )
        db.session.add(new_award)
        db.session.commit()

    return jsonify({"message": "Voice awards calculated and saved."}), 200 

@app.route('/api/voice-exercises', methods=['GET'])
@cross_origin(origins=["http://localhost:3000", "https://capstone-lms.vercel.app", "https://capstone-b5lfpvbba-paragons-projects-6f921143.vercel.app"])
def voice_exercises():
    try:
        student_id = request.args.get('studentId')
        module_title = request.args.get('moduleTitle')

        if not student_id or not module_title:
            return jsonify({'error': 'Student ID and Module title are required'}), 400

        exercises = VoiceExcercises.query.join(Module).filter(Module.moduleTitle == module_title).all()
        
        results = []
        for ex in exercises:
           
            completed_exercise = VoiceExcercisesHistory.query.filter_by(
                studentId=student_id, voiceExercisesId=ex.id, completed=True
            ).first()

            exercise_data = {
                'id': ex.id,
                'voice': ex.voice,
                'grade': ex.grade,
                'voiceImage': ex.voiceImage,
                'isCompleted': completed_exercise is not None,
               
                'scores': {
                    'accuracy_score': completed_exercise.accuracyScore,
                    'pronunciation_score': completed_exercise.pronunciationScore,
                    'fluency_score': completed_exercise.fluencyScore,
                    'speed_score': completed_exercise.speedScore,
                    'final_score': completed_exercise.score,
                    'grade': completed_exercise.grade,
                } if completed_exercise else None
            }
            results.append(exercise_data)

        return jsonify({
            'status': 'success',
            'exercises': results
        }), 200
    except Exception as e:
        print(f"Error fetching voice exercises: {e}")
        return jsonify({'error': 'An error occurred while fetching data.'}), 500

def assign_award(average_score):
    """Helper function to assign award based on average score"""
    if average_score >= 95:
        return "Star Badge"
    elif average_score >= 90:
        return "Gold Badge"
    elif average_score >= 80:
        return "Silver Badge"
    elif average_score >= 70:
        return "Bronze Badge"
    return None

def calculate_student_voice_awards(student_id):
    """Calculate student awards based on voice exercise history"""
  
    voice_history = VoiceExcercisesHistory.query.filter_by(studentId=student_id).all()

    
    if not voice_history:
        return jsonify({"message": "No voice exercise history found for this student."}), 200

    # Calculate total and average scores for voice exercises
    total_voice_score = sum([voice.score for voice in voice_history])
    average_voice_score = total_voice_score / len(voice_history) if voice_history else 0

  
    voice_award = assign_award(average_voice_score)

    
    if voice_award:
        new_award = Award(
          studentId=student_id, 
          awardType=voice_award, 
          tier="Voice Exercises",
          createdAt=datetime.now() 
        )
        db.session.add(new_award)
        db.session.commit()

    return jsonify({"message": "Voice awards calculated and saved."}), 200
        

    if wps < 0.01:
        return 0
    elif 0.01 <= wps < 0.02:
        return 5
    elif 0.02 <= wps < 0.05:
        return 10
    elif 0.05 <= wps < 0.1:
        return 15
    elif 0.1 <= wps < 0.15:
        return 20
    elif 0.15 <= wps < 0.2:
        return 25
    elif 0.2 <= wps < 0.25:
        return 30
    elif 0.25 <= wps < 0.3:
        return 35
    elif 0.3 <= wps < 0.4:
        return 40
    elif 0.4 <= wps < 0.5:
        return 45
    elif 0.5 <= wps < 0.6:
        return 50
    elif 0.6 <= wps < 0.75:
        return 55
    elif 0.75 <= wps < 1.0:
        return 60
    elif 1.0 <= wps < 1.25:
        return 70
    elif 1.25 <= wps < 1.5:
        return 80
    elif 1.5 <= wps < 1.75:
        return 85
    elif 1.75 <= wps < 2.0:
        return 90
    elif 2.0 <= wps < 2.25:
        return 92
    elif 2.25 <= wps < 2.5:
        return 95
    elif 2.5 <= wps < 2.75:
        return 98
    elif 2.75 <= wps < 3.0:
        return 99
    else:
        return 100



def recognize_speech(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio_data = recognizer.record(source)
        return recognizer.recognize_google(audio_data)
    
def get_grade(final_score):
    if final_score >= 90:
        return 'Excellent'
    elif final_score >= 85:
        return 'Very Satisfactory'
    elif final_score >= 80:
        return 'Satisfactory'
    elif final_score >= 75:
        return 'Fairly Satisfactory'
    else:
        return 'Did Not Meet Expectations'

@app.route('/api/voice-exercises-history', methods=['POST'])
def create_voice_exercise_history():
    try:
        if 'audio_blob' in request.files and 'expected_text' in request.form:
            audio_blob = request.files['audio_blob']
            expected_text = request.form['expected_text']
            audio_filename = 'recorded_audio.webm'
            audio_path = os.path.join(app.root_path, 'static', audio_filename)

           
            audio_blob.save(audio_path)

           
            audio = AudioSegment.from_file(audio_path, format="webm")
            wav_filename = 'recorded_audio.wav'
            wav_path = os.path.join(app.root_path, 'static', wav_filename)
            audio.export(wav_path, format="wav")

            try:
                recognized_text = recognize_speech(wav_path)
            except sr.UnknownValueError:
                recognized_text = ""
            except sr.RequestError:
                return jsonify({'error': 'Could not process audio; please try again'})

          


           
         
         
        else:
            return jsonify({'error': 'No audio file or expected text received'}), 400
    except Exception as e:
        app.logger.error(f"Error processing audio: {e}")
        return jsonify({'error': 'An error occurred while processing audio.'}), 500


@app.route('/api/submit-exercise', methods=['POST'])
@cross_origin(origins=["http://localhost:3000", "https://capstone-lms.vercel.app"])
def submit_exercise():
    try:
        data = request.get_json()
        student_id = data.get('student_id')
        voice_exercises_id = data.get('voice_exercises_id')

       
        if not student_id or not voice_exercises_id:
            return jsonify({'error': 'Missing student ID or exercise ID'}), 400

       
        existing_history = VoiceExcercisesHistory.query.filter_by(
            studentId=student_id, voiceExercisesId=voice_exercises_id, completed=True
        ).first()

        if existing_history:
            return jsonify({'error': 'This exercise has already been completed.'}), 400

     
        expected_text = data.get('expected_text')
        voice_image = data.get('voice_image')
        recognized_text = data.get('recognized_text')
        accuracy_score = data.get('accuracy_score')
        pronunciation_score = data.get('pronunciation_score')
        fluency_score = data.get('fluency_score')
        speed_score = data.get('speed_score')
        phonemes = data.get('phonemes')
        final_score = data.get('final_score')
        voice_record = data.get('voiceRecord')
        grade = get_grade(final_score)
       
        new_history = VoiceExcercisesHistory(
            voice=expected_text,
            voiceRecord=voice_record,
            voiceImage=voice_image,
            recognizedText=recognized_text,
            accuracyScore=accuracy_score,
            pronunciationScore=pronunciation_score,
            fluencyScore=fluency_score,
            speedScore=speed_score,
            phonemes=json.dumps(phonemes),
            voiceExercisesId=voice_exercises_id,
            studentId=student_id,
            score=final_score,
            completed=True,
            grade=grade
        )

       
        exercise = VoiceExcercises.query.filter_by(id=voice_exercises_id).first()
        if exercise:
            exercise.completed = True

    
        db.session.add(new_history)
        db.session.commit()

        calculate_student_voice_awards(student_id)

        # Return success response
        return jsonify({'success': True}), 200

    except Exception as e:
        logging.error(f"Error in submit_exercise: {str(e)}")
        return jsonify({'error': 'Failed to submit exercise'}), 500


if __name__ == '__main__':
    with app.app_context():
        db.create_all() 
    app.run(debug=True)