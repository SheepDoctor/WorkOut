package com.example.workout.ui.camera

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import com.google.mlkit.vision.pose.Pose
import com.google.mlkit.vision.pose.PoseLandmark
import kotlin.math.abs
import kotlin.math.pow
import kotlin.math.sqrt

class CameraCoachViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<CameraCoachState>(CameraCoachState.Idle)
    val uiState: StateFlow<CameraCoachState> = _uiState.asStateFlow()
    
    // Reference pose for comparison (would be loaded from selected exercise)
    private var referencePose: Pose? = null
    
    fun analyzePose(pose: Pose) {
        viewModelScope.launch {
            if (pose.allPoseLandmarks.isEmpty()) {
                _uiState.value = CameraCoachState.NoPose
                return@launch
            }
            
            val feedback = if (referencePose != null) {
                comparePoses(pose, referencePose!!)
            } else {
                // Basic form check without reference
                checkBasicForm(pose)
            }
            
            _uiState.value = CameraCoachState.Detecting(feedback)
        }
    }
    
    private fun checkBasicForm(pose: Pose): PoseFeedback {
        val landmarks = pose.allPoseLandmarks
        
        val leftShoulder = landmarks.find { it.landmarkType == PoseLandmark.LEFT_SHOULDER }
        val rightShoulder = landmarks.find { it.landmarkType == PoseLandmark.RIGHT_SHOULDER }
        val leftHip = landmarks.find { it.landmarkType == PoseLandmark.LEFT_HIP }
        val rightHip = landmarks.find { it.landmarkType == PoseLandmark.RIGHT_HIP }
        
        if (leftShoulder == null || rightShoulder == null || leftHip == null || rightHip == null) {
            return PoseFeedback(
                message = "请确保全身在画面中",
                isGood = false
            )
        }
        
        // Check if shoulders are level
        val shoulderDiff = abs(leftShoulder.position.y - rightShoulder.position.y)
        val hipDiff = abs(leftHip.position.y - rightHip.position.y)
        
        val feedback = mutableListOf<String>()
        var isGood = true
        
        if (shoulderDiff > 0.05) {
            feedback.add("肩膀不平，请调整")
            isGood = false
        }
        
        if (hipDiff > 0.05) {
            feedback.add("骨盆不平，请调整")
            isGood = false
        }
        
        return PoseFeedback(
            message = if (feedback.isEmpty()) {
                getString(R.string.good_form)
            } else {
                feedback.joinToString("\n")
            },
            isGood = isGood
        )
    }
    
    private fun comparePoses(current: Pose, reference: Pose): PoseFeedback {
        val currentLandmarks = current.allPoseLandmarks
        val referenceLandmarks = reference.allPoseLandmarks
        
        if (currentLandmarks.size != referenceLandmarks.size) {
            return PoseFeedback(
                message = "姿态不完整，请调整位置",
                isGood = false
            )
        }
        
        var totalError = 0.0
        val feedback = mutableListOf<String>()
        
        // Compare key landmarks
        val keyLandmarks = listOf(
            PoseLandmark.LEFT_SHOULDER,
            PoseLandmark.RIGHT_SHOULDER,
            PoseLandmark.LEFT_ELBOW,
            PoseLandmark.RIGHT_ELBOW,
            PoseLandmark.LEFT_WRIST,
            PoseLandmark.RIGHT_WRIST,
            PoseLandmark.LEFT_HIP,
            PoseLandmark.RIGHT_HIP,
            PoseLandmark.LEFT_KNEE,
            PoseLandmark.RIGHT_KNEE,
            PoseLandmark.LEFT_ANKLE,
            PoseLandmark.RIGHT_ANKLE
        )
        
        for (landmarkType in keyLandmarks) {
            val currentLandmark = currentLandmarks.find { it.landmarkType == landmarkType }
            val referenceLandmark = referenceLandmarks.find { it.landmarkType == landmarkType }
            
            if (currentLandmark != null && referenceLandmark != null) {
                val error = calculateDistance(
                    currentLandmark.position.x,
                    currentLandmark.position.y,
                    referenceLandmark.position.x,
                    referenceLandmark.position.y
                )
                totalError += error
                
                if (error > 0.1) {
                    when (landmarkType) {
                        PoseLandmark.LEFT_SHOULDER, PoseLandmark.RIGHT_SHOULDER ->
                            feedback.add("肩膀位置需要调整")
                        PoseLandmark.LEFT_ELBOW, PoseLandmark.RIGHT_ELBOW ->
                            feedback.add("手肘位置需要调整")
                        PoseLandmark.LEFT_HIP, PoseLandmark.RIGHT_HIP ->
                            feedback.add("髋部位置需要调整")
                        PoseLandmark.LEFT_KNEE, PoseLandmark.RIGHT_KNEE ->
                            feedback.add("膝盖位置需要调整")
                    }
                }
            }
        }
        
        val avgError = totalError / keyLandmarks.size
        val isGood = avgError < 0.08 && feedback.isEmpty()
        
        return PoseFeedback(
            message = if (isGood) {
                getString(R.string.good_form)
            } else if (feedback.isEmpty()) {
                getString(R.string.adjust_form)
            } else {
                feedback.distinct().joinToString("\n")
            },
            isGood = isGood
        )
    }
    
    private fun calculateDistance(x1: Float, y1: Float, x2: Float, y2: Float): Double {
        return sqrt((x1 - x2).toDouble().pow(2) + (y1 - y2).toDouble().pow(2))
    }
    
    fun handleError(message: String) {
        _uiState.value = CameraCoachState.Error(message)
    }
    
    fun setReferencePose(pose: Pose) {
        referencePose = pose
    }
    
    private fun getString(resId: Int): String {
        // In real implementation, use string resources properly
        return when (resId) {
            com.example.workout.R.string.good_form -> "动作标准"
            com.example.workout.R.string.adjust_form -> "请调整动作"
            else -> ""
        }
    }
}

sealed class CameraCoachState {
    object Idle : CameraCoachState()
    data class Detecting(val feedback: PoseFeedback) : CameraCoachState()
    object NoPose : CameraCoachState()
    data class Error(val message: String) : CameraCoachState()
}

data class PoseFeedback(
    val message: String,
    val isGood: Boolean
)

