package com.example.workout.ui.camera

import android.os.Bundle
import android.util.Log
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
import androidx.navigation.fragment.findNavController
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
    companion object {
        private const val TAG = "CameraCoachFragment"
    }
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
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d(TAG, "onCreate")
    }
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        Log.d(TAG, "onCreateView: Starting")
        try {
            _binding = FragmentCameraCoachBinding.inflate(inflater, container, false)
            Log.d(TAG, "onCreateView: Binding inflated successfully")
            return binding.root
        } catch (e: Exception) {
            Log.e(TAG, "onCreateView: Error inflating layout", e)
            throw e
        }
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        Log.d(TAG, "onViewCreated: Starting")
        
        try {
            cameraExecutor = Executors.newSingleThreadExecutor()
            Log.d(TAG, "onViewCreated: Camera executor created")
            
            binding.toolbar.setNavigationOnClickListener {
                Log.d(TAG, "onViewCreated: Toolbar back button clicked")
                try {
                    findNavController().navigateUp()
                } catch (e: Exception) {
                    Log.e(TAG, "onViewCreated: Error navigating up", e)
                }
            }
            
            binding.btnStart.setOnClickListener {
                Log.d(TAG, "onViewCreated: Start button clicked")
                try {
                    startCamera()
                    binding.btnStart.visibility = View.GONE
                    binding.btnStop.visibility = View.VISIBLE
                } catch (e: Exception) {
                    Log.e(TAG, "onViewCreated: Error starting camera", e)
                }
            }
            
            binding.btnStop.setOnClickListener {
                Log.d(TAG, "onViewCreated: Stop button clicked")
                try {
                    stopCamera()
                    binding.btnStart.visibility = View.VISIBLE
                    binding.btnStop.visibility = View.GONE
                } catch (e: Exception) {
                    Log.e(TAG, "onViewCreated: Error stopping camera", e)
                }
            }
        
            // Observe ViewModel state
            Log.d(TAG, "onViewCreated: Setting up ViewModel observer")
            viewLifecycleOwner.lifecycleScope.launch {
                try {
                    viewModel.uiState.collect { state ->
                        Log.d(TAG, "onViewCreated: ViewModel state changed: $state")
                        if (!isAdded || _binding == null) {
                            Log.w(TAG, "onViewCreated: Fragment not added or binding null, skipping update")
                            return@collect
                        }
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
                                Log.e(TAG, "onViewCreated: ViewModel error state: ${state.message}")
                                binding.tvStatus.text = "错误: ${state.message}"
                            }
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "onViewCreated: Error observing ViewModel state", e)
                }
            }
            Log.d(TAG, "onViewCreated: Completed successfully")
        } catch (e: Exception) {
            Log.e(TAG, "onViewCreated: Error setting up views", e)
            throw e
        }
    }
    
    private fun startCamera() {
        Log.d(TAG, "startCamera: Starting")
        if (!isAdded || _binding == null) {
            Log.w(TAG, "startCamera: Fragment not added or binding null, returning")
            return
        }
        
        try {
            Log.d(TAG, "startCamera: Getting camera provider")
            val cameraProviderFuture = ProcessCameraProvider.getInstance(requireContext())
            
            cameraProviderFuture.addListener({
                Log.d(TAG, "startCamera: Camera provider future listener called")
                if (!isAdded || _binding == null) {
                    Log.w(TAG, "startCamera: Fragment not added or binding null in listener, returning")
                    return@addListener
                }
                
                try {
                    Log.d(TAG, "startCamera: Getting camera provider from future")
                    val cameraProvider: ProcessCameraProvider = cameraProviderFuture.get()
                    Log.d(TAG, "startCamera: Camera provider obtained")
                    
                    Log.d(TAG, "startCamera: Building preview")
                    val preview = Preview.Builder().build().also {
                        it.setSurfaceProvider(binding.previewView.surfaceProvider)
                    }
                    
                    Log.d(TAG, "startCamera: Building image analyzer")
                    imageAnalyzer = ImageAnalysis.Builder()
                        .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                        .build()
                        .also {
                            it.setAnalyzer(cameraExecutor) { imageProxy ->
                                analyzeImage(imageProxy)
                            }
                        }
                    
                    Log.d(TAG, "startCamera: Building image capture")
                    imageCapture = ImageCapture.Builder().build()
                    
                    val cameraSelector = CameraSelector.DEFAULT_BACK_CAMERA
                    Log.d(TAG, "startCamera: Unbinding all cameras")
                    cameraProvider.unbindAll()
                    
                    Log.d(TAG, "startCamera: Binding camera to lifecycle")
                    camera = cameraProvider.bindToLifecycle(
                        viewLifecycleOwner,
                        cameraSelector,
                        preview,
                        imageAnalyzer,
                        imageCapture
                    )
                    Log.d(TAG, "startCamera: Camera started successfully")
                } catch (e: Exception) {
                    Log.e(TAG, "startCamera: Error in listener", e)
                    if (isAdded) {
                        viewModel.handleError(e.message ?: "启动摄像头失败")
                    }
                }
            }, ContextCompat.getMainExecutor(requireContext()))
            Log.d(TAG, "startCamera: Listener added to camera provider future")
        } catch (e: Exception) {
            Log.e(TAG, "startCamera: Error getting camera provider", e)
            if (isAdded) {
                viewModel.handleError(e.message ?: "启动摄像头失败")
            }
        }
    }
    
    private fun stopCamera() {
        Log.d(TAG, "stopCamera: Starting")
        if (!isAdded) {
            Log.w(TAG, "stopCamera: Fragment not added, returning")
            return
        }
        
        try {
            val cameraProviderFuture = ProcessCameraProvider.getInstance(requireContext())
            cameraProviderFuture.addListener({
                if (!isAdded) {
                    Log.w(TAG, "stopCamera: Fragment not added in listener, returning")
                    return@addListener
                }
                try {
                    Log.d(TAG, "stopCamera: Unbinding camera")
                    val cameraProvider = cameraProviderFuture.get()
                    cameraProvider.unbindAll()
                    Log.d(TAG, "stopCamera: Camera stopped successfully")
                } catch (e: Exception) {
                    Log.w(TAG, "stopCamera: Camera provider already unbound or not initialized", e)
                }
            }, ContextCompat.getMainExecutor(requireContext()))
        } catch (e: Exception) {
            Log.e(TAG, "stopCamera: Error stopping camera", e)
        }
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
        if (!isAdded || _binding == null) return
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
    
    override fun onStart() {
        super.onStart()
        Log.d(TAG, "onStart")
    }
    
    override fun onResume() {
        super.onResume()
        Log.d(TAG, "onResume")
    }
    
    override fun onPause() {
        super.onPause()
        Log.d(TAG, "onPause")
    }
    
    override fun onStop() {
        super.onStop()
        Log.d(TAG, "onStop")
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        Log.d(TAG, "onDestroyView: Starting cleanup")
        try {
            stopCamera()
            if (::cameraExecutor.isInitialized) {
                Log.d(TAG, "onDestroyView: Shutting down camera executor")
                cameraExecutor.shutdown()
            }
            imageAnalyzer?.clearAnalyzer()
            _binding = null
            Log.d(TAG, "onDestroyView: Cleanup completed")
        } catch (e: Exception) {
            Log.e(TAG, "onDestroyView: Error during cleanup", e)
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "onDestroy")
    }
}

