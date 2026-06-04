from collections import deque

from ai_engine.config.attention_thresholds import AttentionThresholds
from focuslens.types import AttentionState, FrameMetrics


class AttentionScorer:
    """Combines detector signals into a smoothed 0-100 attention score."""

    def __init__(self, thresholds: AttentionThresholds | None = None) -> None:
        self.config = thresholds or AttentionThresholds()
        self._gaze_history: deque[bool] = deque(
            maxlen=max(1, self.config.distraction_window_frames)
        )
        self._smoothed_score: float | None = None

    def score(
        self,
        *,
        face_present: bool,
        eyes_open: bool,
        gaze_forward: bool,
        head_upright: bool,
        drowsy: bool,
    ) -> FrameMetrics:
        distracted = self._update_distraction_state(face_present, gaze_forward)

        components = {
            "face": 1.0 if face_present else 0.0,
            "eyes": 1.0 if face_present and eyes_open else 0.0,
            "gaze": 1.0 if face_present and gaze_forward else 0.0,
            "posture": 1.0 if face_present and head_upright else 0.0,
            "alertness": 1.0 if face_present and not drowsy else 0.0,
        }

        raw_attention = self._raw_attention_score(components, face_present)
        adjusted_attention = self._apply_state_adjustments(
            raw_attention=raw_attention,
            face_present=face_present,
            distracted=distracted,
            drowsy=drowsy,
        )
        attention = self._smooth_score(
            adjusted_attention,
            face_present=face_present,
            drowsy=drowsy,
        )
        attention_state = self._classify(
            face_present=face_present,
            drowsy=drowsy,
            distracted=distracted,
            attention_score=attention,
        )

        return FrameMetrics(
            face_present=face_present,
            eyes_open=eyes_open,
            gaze_forward=gaze_forward,
            head_upright=head_upright,
            drowsy=drowsy,
            distracted=distracted,
            attention_state=attention_state,
            raw_attention_score=raw_attention,
            attention_score=attention,
            components=components,
            landmarks_detected=face_present,
        )

    def _update_distraction_state(self, face_present: bool, gaze_forward: bool) -> bool:
        if not face_present:
            self._gaze_history.clear()
            return False

        self._gaze_history.append(gaze_forward)
        if len(self._gaze_history) < self.config.distraction_min_frames:
            return False

        away_count = sum(1 for gaze in self._gaze_history if not gaze)
        away_ratio = away_count / len(self._gaze_history)
        return away_ratio > self.config.distraction_ratio_threshold

    def _raw_attention_score(
        self,
        components: dict[str, float],
        face_present: bool,
    ) -> float:
        if not face_present:
            return self.config.inactive_score
        weighted_score = sum(
            components[key] * self.config.weights[key] for key in self.config.weights
        )
        return self._clamp_score(weighted_score * 100.0)

    def _apply_state_adjustments(
        self,
        *,
        raw_attention: float,
        face_present: bool,
        distracted: bool,
        drowsy: bool,
    ) -> float:
        if not face_present:
            return self.config.inactive_score

        score = raw_attention
        if distracted:
            score *= self.config.distraction_score_penalty
        if drowsy:
            score = min(score, self.config.drowsy_score_cap)
        return self._clamp_score(score)

    def _smooth_score(
        self,
        score: float,
        *,
        face_present: bool,
        drowsy: bool,
    ) -> float:
        if not face_present:
            self._smoothed_score = self.config.inactive_score
            return self.config.inactive_score
        if drowsy:
            self._smoothed_score = score
            return self._clamp_score(score)

        if self._smoothed_score is None:
            self._smoothed_score = score
            return self._clamp_score(score)

        alpha = min(max(self.config.score_smoothing_alpha, 0.0), 1.0)
        self._smoothed_score = alpha * score + (1.0 - alpha) * self._smoothed_score
        return self._clamp_score(self._smoothed_score)

    def _classify(
        self,
        *,
        face_present: bool,
        drowsy: bool,
        distracted: bool,
        attention_score: float,
    ) -> AttentionState:
        if not face_present:
            return AttentionState.INACTIVE
        if drowsy:
            return AttentionState.DROWSY
        if distracted or attention_score < self.config.focused_min_score:
            return AttentionState.DISTRACTED
        return AttentionState.FOCUSED

    @staticmethod
    def _clamp_score(score: float) -> float:
        return max(0.0, min(100.0, score))

    def reset(self) -> None:
        self._gaze_history.clear()
        self._smoothed_score = None
