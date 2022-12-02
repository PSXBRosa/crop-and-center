import dlib
import os
from typing import Iterable, Tuple, List, Any
from numpy.typing import ArrayLike
import cv2

class Picture():
    def __init__(self, path : str) -> None:
        self.path = path
        self.fig : ArrayLike[int] = cv2.imread(path)
        assert self.fig is not None, f"Impossible to open figure at {path}"

    def find_face(self) -> List[Tuple[List, int, int, int ,int]]:
        """
        finds the position of the eyes and the size of the face in the figure
        """
        
        # loads trained classifiers
        parent_dir = os.path.dirname(__file__)
        face_detector = dlib.get_frontal_face_detector()
        feature_xtrct = dlib.shape_predictor(parent_dir+"\models\shape_predictor_68_face_landmarks.dat")

        # detects faces
        faces = face_detector(self.fig)

        out = []
        for rect in faces:
            center = rect.center()
            (x,y), h, w = (center.x, center.y), rect.height(), rect.width()

            # for each face, finds the eyes
            features = feature_xtrct(self.fig, rect)
            eye1 = (features.part(40).x + features.part(37).x)/2, (features.part(40).y + features.part(37).y)/2
            eye2 = (features.part(43).x + features.part(46).x)/2, (features.part(43).y + features.part(46).y)/2

            out.append( ([eye1, eye2], x, y, w, h) )

        return out

    def rotate(self, point : Tuple[int, int], angle : float):
        """
        rotates image by a given angle (in radians) around a point
        """
        rot_mat = cv2.getRotationMatrix2D(point, angle, 1.0)
        self.fig = cv2.warpAffine(self.fig, rot_mat, point, flags=cv2.INTER_LINEAR)

    def crop(self, center : Tuple[int, int], h : int, w : int) -> None:
        """
        crops image around center
        """
        x,y = center
        self.fig = self.fig[y-h//2:y+h//2, x-w//2:x+w//2]

    def resize(self, w : int, h : int) -> None:
        """
        resizes image to desired values
        """
        self.fig = cv2.resize(self.fig, (w,h))

    def save(self, path : str) -> None:
        """
        saves picture at path
        """
        cv2.imwrite(path, self.fig)

    def copy(self) -> Any:
        """
        creates a deepcopy of self
        """
        return Picture(self.path)

    @property
    def h(self) -> int:
        h : int = len(self.fig)
        return h
    
    @property
    def w(self) -> int:
        w : int = len(self.fig[0])
        return w