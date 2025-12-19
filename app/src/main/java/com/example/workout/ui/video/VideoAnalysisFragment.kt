package com.example.workout.ui.video

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import com.example.workout.databinding.FragmentVideoAnalysisBinding
import kotlinx.coroutines.launch

class VideoAnalysisFragment : Fragment() {
    private var _binding: FragmentVideoAnalysisBinding? = null
    private val binding get() = _binding!!
    
    private val args: VideoAnalysisFragmentArgs by navArgs()
    private val viewModel: VideoAnalysisViewModel by viewModels()
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentVideoAnalysisBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        binding.toolbar.setNavigationOnClickListener {
            findNavController().navigateUp()
        }
        
        // Load video URI from args
        val videoUri = args.videoUri
        if (videoUri.isNotEmpty()) {
            viewModel.analyzeVideo(videoUri)
        }
        
        binding.btnAnalyze.setOnClickListener {
            val url = binding.etVideoUrl.text.toString()
            if (url.isNotEmpty()) {
                viewModel.analyzeVideo(url)
            } else {
                Toast.makeText(requireContext(), "请输入视频链接", Toast.LENGTH_SHORT).show()
            }
        }
        
        binding.btnGenerateNote.setOnClickListener {
            viewModel.generateNote()
        }
        
        // Observe ViewModel state
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.uiState.collect { state ->
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
                        val action = VideoAnalysisFragmentDirections
                            .actionVideoAnalysisToNoteDetail(state.noteId)
                        findNavController().navigate(action)
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
        }
    }
    
    private fun displayAnalysisResults(exercises: List<Exercise>) {
        // Display exercises in RecyclerView or other UI component
        // This is a placeholder - you would implement proper UI here
        binding.tvStatus.text = "检测到 ${exercises.size} 个动作"
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

