class FaceDetector:
    """Face presence is inferred from successful landmark detection."""

    @staticmethod
    def is_face_present(landmarks) -> bool:
        return landmarks is not None
