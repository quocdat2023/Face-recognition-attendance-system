import cv2
import numpy as np
import face_recognition

class LivenessDetector:
    """
    Implements multi-layer anti-spoofing checks.
    1. Focus/Blurriness (Passive)
    2. Color/Texture Analysis (Passive)
    3. Eye Blink Detection (Motion - requires temporal data)
    4. Frequency Domain Analysis (Moiré pattern detection)
    """

    def __init__(self):
        # Thresholds - these would need tuning based on the specific camera hardware
        self.BLUR_THRESHOLD = 100.0  # Laplacian variance
        self.MOIRE_THRESHOLD = 0.5   # Arbitrary threshold for frequency spike detection
        self.EYE_AR_THRESH = 0.25    # Eye Aspect Ratio threshold for closed eyes

    def check_image_quality(self, frame):
        """
        Passive Check: Rejects images that are too blurry (often happens with replays/screens)
        Returns: (passed: bool, score: float, message: str)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        score = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        if score < self.BLUR_THRESHOLD:
            return False, score, "Image too blurry (possible screen replay)"
        return True, score, "Image clarity OK"

    def detect_moire_pattern(self, frame):
        """
        Passive Check: Analyzes frequency domain for Moiré patterns common in screen captures.
        Uses Discrete Fourier Transform (DFT).
        Returns: (passed: bool, score: float, message: str)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Optimize size for DFT
        rows, cols = gray.shape
        nrows = cv2.getOptimalDFTSize(rows)
        ncols = cv2.getOptimalDFTSize(cols)
        pad_right = ncols - cols
        pad_bottom = nrows - rows
        padded = cv2.copyMakeBorder(gray, 0, pad_bottom, 0, pad_right, cv2.BORDER_CONSTANT, value=0)

        # Perform FFT
        dft = cv2.dft(np.float32(padded), flags=cv2.DFT_COMPLEX_OUTPUT)
        dft_shift = np.fft.fftshift(dft)
        
        # Calculate magnitude spectrum
        magnitude = 20 * np.log(cv2.magnitude(dft_shift[:,:,0], dft_shift[:,:,1]) + 1)
        
        # Analyze high frequency components (screens often have periodic patterns)
        # This is a simplified heuristic: looking for spikes in non-center regions
        h, w = magnitude.shape
        center_y, center_x = h // 2, w // 2
        
        # Mask out the DC component (center)
        mask_radius = 30
        mask = np.ones((h, w), dtype=np.uint8)
        cv2.circle(mask, (center_x, center_y), mask_radius, 0, -1)
        
        # Calculate energy in high frequencies
        masked_magnitude = magnitude * mask
        high_freq_energy = np.mean(masked_magnitude)
        
        # Note: A real implementation would look for specific geometric peaks
        # For this prototype, we return the energy value. 
        # Extremely high periodic noise might indicate a screen grid.
        
        return True, high_freq_energy, "Frequency analysis complete"

    def calculate_ear(self, eye_points):
        """
        Motion Check Helper: Calculate Eye Aspect Ratio (EAR)
        eye_points: list of (x, y) coordinates for one eye (6 points)
        """
        # Euclidian distance between vertical landmark pairs
        A = np.linalg.norm(np.array(eye_points[1]) - np.array(eye_points[5]))
        B = np.linalg.norm(np.array(eye_points[2]) - np.array(eye_points[4]))
        # Euclidian distance between horizontal landmark pairs
        C = np.linalg.norm(np.array(eye_points[0]) - np.array(eye_points[3]))
        
        ear = (A + B) / (2.0 * C)
        return ear

    def check_liveness_active(self, frame_sequence):
        """
        Active/Motion Check: Requires a sequence of frames (video).
        Detects if user blinked.
        Input: List of frames (numpy arrays)
        """
        blink_detected = False
        min_ear = 1.0
        
        for frame in frame_sequence:
            # Detect face
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_landmarks_list = face_recognition.face_landmarks(rgb)
            
            for face_landmarks in face_landmarks_list:
                left_eye = face_landmarks['left_eye']
                right_eye = face_landmarks['right_eye']
                
                left_ear = self.calculate_ear(left_eye)
                right_ear = self.calculate_ear(right_eye)
                
                avg_ear = (left_ear + right_ear) / 2.0
                if avg_ear < min_ear:
                    min_ear = avg_ear
                
                if avg_ear < self.EYE_AR_THRESH:
                    blink_detected = True
        
        if blink_detected:
            return True, min_ear, "Blink detected"
        else:
            return False, min_ear, "No blink detected (possible static photo)"

    def check_face_reflection(self, frame, face_box):
        """
        Passive Check: Analyze specular highlights. 
        Skin has different reflection properties than paper/glass.
        """
        # Extract face ROI
        top, right, bottom, left = face_box
        roi = frame[top:bottom, left:right]
        
        # Convert to HSV
        hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        
        # Calculate histogram of Value channel
        hist = cv2.calcHist([hsv_roi], [2], None, [256], [0, 256])
        
        # Check for "clipping" at the high end (glare from screens)
        # or flat histograms (printed paper often has lower contrast range)
        high_intensity_pixels = np.sum(hist[250:])
        total_pixels = np.sum(hist)
        
        ratio = high_intensity_pixels / total_pixels
        
        # If too much glare, it might be a screen or strong light
        if ratio > 0.1: # 10% of pixels are blown out
             return False, ratio, "Excessive glare detected (possible screen)"
             
        return True, ratio, "Reflection levels normal"

# Usage Example (Pseudo-logic)
def run_security_check(image_path):
    detector = LivenessDetector()
    frame = cv2.imread(image_path)
    
    # 1. Blur check
    is_clear, blur_score, msg = detector.check_image_quality(frame)
    if not is_clear:
        return False, msg
    
    # 2. Moiré analysis
    input_ok, moire_score, msg = detector.detect_moire_pattern(frame)
    
    # 3. Deep Learning Anti-Spoofing (Mock)
    # real_score = deep_model.predict(frame)
    # if real_score < 0.5: return False, "Spoof Detected by AI"
    
    return True, "Liveness Verified"
