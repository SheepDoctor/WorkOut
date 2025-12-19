package com.example.workout.ui.home

import android.Manifest
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.example.workout.R
import com.example.workout.databinding.FragmentHomeBinding

class HomeFragment : Fragment() {
    companion object {
        private const val TAG = "HomeFragment"
    }
    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!
    
    private val requestVideoLauncher = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let {
            // Navigate to video analysis with video URI
            val bundle = Bundle().apply {
                putString("videoUri", it.toString())
            }
            findNavController().navigate(R.id.action_home_to_video_analysis, bundle)
        }
    }
    
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
            _binding = FragmentHomeBinding.inflate(inflater, container, false)
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
            binding.btnVideoAnalysis.setOnClickListener {
                Log.d(TAG, "onViewCreated: btnVideoAnalysis clicked")
                if (checkStoragePermission()) {
                    requestVideoLauncher.launch("video/*")
                } else {
                    requestStoragePermission()
                }
            }
        
            binding.btnCameraCoach.setOnClickListener {
                Log.d(TAG, "onViewCreated: btnCameraCoach clicked")
                try {
                    if (checkCameraPermission()) {
                        Log.d(TAG, "onViewCreated: Camera permission granted, navigating")
                        findNavController().navigate(R.id.action_home_to_camera_coach)
                    } else {
                        Log.d(TAG, "onViewCreated: Camera permission not granted, requesting")
                        requestCameraPermission()
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "onViewCreated: Error navigating to camera coach", e)
                }
            }
            
            binding.btnMyNotes.setOnClickListener {
                Log.d(TAG, "onViewCreated: btnMyNotes clicked")
                try {
                    findNavController().navigate(R.id.action_home_to_notes)
                } catch (e: Exception) {
                    Log.e(TAG, "onViewCreated: Error navigating to notes", e)
                }
            }
            Log.d(TAG, "onViewCreated: Completed successfully")
        } catch (e: Exception) {
            Log.e(TAG, "onViewCreated: Error setting up views", e)
            throw e
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
    
    private fun checkStoragePermission(): Boolean {
        return if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            ContextCompat.checkSelfPermission(
                requireContext(),
                Manifest.permission.READ_MEDIA_VIDEO
            ) == PackageManager.PERMISSION_GRANTED
        } else {
            ContextCompat.checkSelfPermission(
                requireContext(),
                Manifest.permission.READ_EXTERNAL_STORAGE
            ) == PackageManager.PERMISSION_GRANTED
        }
    }
    
    private fun checkCameraPermission(): Boolean {
        return ContextCompat.checkSelfPermission(
            requireContext(),
            Manifest.permission.CAMERA
        ) == PackageManager.PERMISSION_GRANTED
    }
    
    private val storagePermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            requestVideoLauncher.launch("video/*")
        } else {
            Toast.makeText(
                requireContext(),
                getString(R.string.storage_permission_required),
                Toast.LENGTH_SHORT
            ).show()
        }
    }
    
    private val cameraPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            findNavController().navigate(R.id.action_home_to_camera_coach)
        } else {
            Toast.makeText(
                requireContext(),
                getString(R.string.camera_permission_required),
                Toast.LENGTH_SHORT
            ).show()
        }
    }
    
    private fun requestStoragePermission() {
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.TIRAMISU) {
            storagePermissionLauncher.launch(Manifest.permission.READ_MEDIA_VIDEO)
        } else {
            storagePermissionLauncher.launch(Manifest.permission.READ_EXTERNAL_STORAGE)
        }
    }
    
    private fun requestCameraPermission() {
        cameraPermissionLauncher.launch(Manifest.permission.CAMERA)
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        Log.d(TAG, "onDestroyView")
        _binding = null
    }
    
    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "onDestroy")
    }
}

