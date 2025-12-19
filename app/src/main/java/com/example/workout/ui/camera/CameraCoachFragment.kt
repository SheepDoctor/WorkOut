package com.example.workout.ui.camera

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.camera.core.*
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import com.example.workout.R
import com.example.workout.databinding.FragmentCameraCoachBinding
import com.google.mlkit.vision.pose.Pose
import com.google.mlkit.vision.pose.PoseDetection
import com.google.mlkit.vision.pose.PoseLandmark
import com.google.mlkit.vision.pose.accurate.AccuratePoseDetectorOptions
import kotlinx.coroutines.launch
import java.util.concurrent.ExecutorService
import java.util.concurrent.Executors

class CameraCoachFragment : Fragment() {
    private var _binding: FragmentCameraCoachBinding? = null
    private val binding get() = _binding!!
    
    private val viewModel: CameraCoachViewModel by viewModels()
    private var imageCapture: ImageCapture? = null
    private var imageAnalyzer: ImageAnalysis? = null
    private var camera: Camera? = null
    private lateinit var cameraExecutor: ExecutorService
    
    private val poseDetector = PoseDetection.getClient(
        AccuratePoseDetectorOptions.Builder()
            .setDetectorMode(AccuratePoseDetectorOptions.STREAM_MODE)
            .build()
    )
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentCameraCoachBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        cameraExecutor = Executors.newSingleThreadExecutor()
        
        binding.toolbar.setNavigationOnClickListener {
            requireActivity().onBackPressed()
        }
        
        binding.btnStart.setOnClickListener {
            startCamera()
            binding.btnStart.visibility = View.GONE
            binding.btnStop.visibility = View.VISIBLE
        }
        
        binding.btnStop.setOnClickListener {
            stopCamera()
            binding.btnStart.visibility = View.VISIBLE
            binding.btnStop.visibility = View.GONE
        }
        
        // Observe ViewModel state
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                when (state) {
                    is CameraCoachState.Idle -> {
                        binding.tvStatus.text = "准备就绪"
                        binding.tvFeedback.text = ""
                    }
                    is CameraCoachState.Detecting -> {
                        binding.tvStatus.text = getString(R.string.pose_detected)
                        updateFeedback(state.feedback)
                    }
                    is CameraCoachState.NoPose -> {
                        binding.tvStatus.text = getString(R.string.pose_not_detected)
                        binding.tvFeedback.text = "请站在摄像头前"
                    }
                    is CameraCoachState.Error -> {
                        binding.tvStatus.text = "错误: ${state.message}"
                    }
                }
            }
        }
    }
    
    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(requireContext())
        
        cameraProviderFuture.addListener({
            val cameraProvider: ProcessCameraProvider = cameraProviderFuture.get()
            
            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(binding.previewView.surfaceProvider)
            }
            
            imageAnalyzer = ImageAnalysis.Builder()
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build()
                .also {
                    it.setAnalyzer(cameraExecutor) { imageProxy ->
                        analyzeImage(imageProxy)
                    }
                }
            
            imageCapture = ImageCapture.Builder().build()
            
            val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
            
            try {
                cameraProvider.unbindAll()
                camera = cameraProvider.bindToLifecycle(
                    this,
                    cameraSelector,
                    preview,
                    imageAnalyzer,
                    imageCapture
                )
            } catch (e: Exception) {
                viewModel.handleError(e.message ?: "启动摄像头失败")
            }
        }, ContextCompat.getMainExecutor(requireContext()))
    }
    
    private fun stopCamera() {
        val cameraProvider = ProcessCameraProvider.getInstance(requireContext()).get()
        cameraProvider.unbindAll()
    }
    
    private fun analyzeImage(imageProxy: ImageProxy) {
        val mediaImage = imageProxy.image
        if (mediaImage != null) {
            val image = com.google.mlkit.vision.common.InputImage.fromMediaImage(
                mediaImage,
                imageProxy.imageInfo.rotationDegrees
            )
            
            poseDetector.process(image)
                .addOnSuccessListener { pose ->
                    viewModel.analyzePose(pose)
                    imageProxy.close()
                }
                .addOnFailureListener { e ->
                    viewModel.handleError(e.message ?: "姿态检测失败")
                    imageProxy.close()
                }
        } else {
            imageProxy.close()
        }
    }
    
    private fun updateFeedback(feedback: PoseFeedback) {
        binding.tvFeedback.text = feedback.message
        if (feedback.isGood) {
            binding.tvFeedback.setTextColor(
                ContextCompat.getColor(requireContext(), com.example.workout.R.color.secondary)
            )
        } else {
            binding.tvFeedback.setTextColor(
                ContextCompat.getColor(requireContext(), com.example.workout.R.color.error)
            )
        }
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        cameraExecutor.shutdown()
        _binding = null
    }
}

