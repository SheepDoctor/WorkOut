package com.example.workout.ui.video

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import com.example.workout.R
import com.example.workout.data.model.Exercise
import com.example.workout.databinding.FragmentVideoAnalysisBinding
import kotlinx.coroutines.launch

class VideoAnalysisFragment : Fragment() {
    companion object {
        private const val TAG = "VideoAnalysisFragment"
    }
    private var _binding: FragmentVideoAnalysisBinding? = null
    private val binding get() = _binding!!
    
    private val viewModel: VideoAnalysisViewModel by viewModels()
    
    private val videoUri: String
        get() = arguments?.getString("videoUri") ?: ""
    
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
            _binding = FragmentVideoAnalysisBinding.inflate(inflater, container, false)
            Log.d(TAG, "onCreateView: Binding inflated successfully")
            return binding.root
        } catch (e: Exception) {
            Log.e(TAG, "onCreateView: Error inflating layout", e)
            throw e
        }
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        Log.d(TAG, "onViewCreated: Starting, videoUri: $videoUri")
        
        try {
            binding.toolbar.setNavigationOnClickListener {
                Log.d(TAG, "onViewCreated: Toolbar back button clicked")
                try {
                    findNavController().navigateUp()
                } catch (e: Exception) {
                    Log.e(TAG, "onViewCreated: Error navigating up", e)
                }
            }
            
            // Load video URI from args
            if (videoUri.isNotEmpty()) {
                Log.d(TAG, "onViewCreated: Auto-analyzing video with URI: $videoUri")
                viewModel.analyzeVideo(videoUri)
            }
            
            binding.btnAnalyze.setOnClickListener {
                Log.d(TAG, "onViewCreated: Analyze button clicked")
                val url = binding.etVideoUrl.text.toString()
                if (url.isNotEmpty()) {
                    viewModel.analyzeVideo(url)
                } else {
                    Toast.makeText(requireContext(), "请输入视频链接", Toast.LENGTH_SHORT).show()
                }
            }
            
            binding.btnGenerateNote.setOnClickListener {
                Log.d(TAG, "onViewCreated: Generate note button clicked")
                viewModel.generateNote()
            }
            
            // Observe ViewModel state
            viewLifecycleOwner.lifecycleScope.launch {
                try {
                    viewModel.uiState.collect { state ->
                        Log.d(TAG, "onViewCreated: ViewModel state changed: $state")
                        when (state) {
                            is VideoAnalysisState.Idle -> {
                                binding.progressBar.visibility = View.GONE
                                binding.btnAnalyze.isEnabled = true
                            }
                            is VideoAnalysisState.Analyzing -> {
                                binding.progressBar.visibility = View.VISIBLE
                                binding.btnAnalyze.isEnabled = false
                                binding.tvStatus.text = getString(R.string.analyzing)
                            }
                            is VideoAnalysisState.Analyzed -> {
                                binding.progressBar.visibility = View.GONE
                                binding.btnAnalyze.isEnabled = true
                                binding.btnGenerateNote.isEnabled = true
                                binding.tvStatus.text = "分析完成"
                                displayAnalysisResults(state.exercises)
                            }
                            is VideoAnalysisState.GeneratingNote -> {
                                binding.progressBar.visibility = View.VISIBLE
                                binding.tvStatus.text = "生成笔记中..."
                            }
                            is VideoAnalysisState.NoteGenerated -> {
                                binding.progressBar.visibility = View.GONE
                                Toast.makeText(
                                    requireContext(),
                                    "笔记生成成功",
                                    Toast.LENGTH_SHORT
                                ).show()
                                // Navigate to notes detail
                                val bundle = Bundle().apply {
                                    putString("noteId", state.noteId)
                                }
                                findNavController().navigate(R.id.action_video_analysis_to_note_detail, bundle)
                            }
                            is VideoAnalysisState.Error -> {
                                binding.progressBar.visibility = View.GONE
                                binding.btnAnalyze.isEnabled = true
                                binding.tvStatus.text = "错误: ${state.message}"
                                Toast.makeText(
                                    requireContext(),
                                    state.message,
                                    Toast.LENGTH_SHORT
                                ).show()
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
    
    private fun displayAnalysisResults(exercises: List<Exercise>) {
        Log.d(TAG, "displayAnalysisResults: Displaying ${exercises.size} exercises")
        // Display exercises in RecyclerView or other UI component
        // This is a placeholder - you would implement proper UI here
        binding.tvStatus.text = "检测到 ${exercises.size} 个动作"
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

