package com.example.workout.ui.notes

import android.os.Bundle
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import com.example.workout.data.model.WorkoutNote
import com.example.workout.databinding.FragmentNoteDetailBinding
import kotlinx.coroutines.launch

class NoteDetailFragment : Fragment() {
    companion object {
        private const val TAG = "NoteDetailFragment"
    }
    private var _binding: FragmentNoteDetailBinding? = null
    private val binding get() = _binding!!
    
    private val viewModel: NoteDetailViewModel by viewModels()
    
    private val noteId: String
        get() = arguments?.getString("noteId") ?: ""
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d(TAG, "onCreate, noteId: $noteId")
    }
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        Log.d(TAG, "onCreateView: Starting")
        try {
            _binding = FragmentNoteDetailBinding.inflate(inflater, container, false)
            Log.d(TAG, "onCreateView: Binding inflated successfully")
            return binding.root
        } catch (e: Exception) {
            Log.e(TAG, "onCreateView: Error inflating layout", e)
            throw e
        }
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        Log.d(TAG, "onViewCreated: Starting, noteId: $noteId")
        
        try {
            binding.toolbar.setNavigationOnClickListener {
                Log.d(TAG, "onViewCreated: Toolbar back button clicked")
                try {
                    findNavController().navigateUp()
                } catch (e: Exception) {
                    Log.e(TAG, "onViewCreated: Error navigating up", e)
                }
            }
            
            viewLifecycleOwner.lifecycleScope.launch {
                try {
                    viewModel.note.collect { note ->
                        Log.d(TAG, "onViewCreated: Note updated: $note")
                        note?.let {
                            displayNote(it)
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "onViewCreated: Error observing note", e)
                }
            }
            
            viewModel.loadNote(noteId)
            Log.d(TAG, "onViewCreated: Completed successfully")
        } catch (e: Exception) {
            Log.e(TAG, "onViewCreated: Error setting up views", e)
            throw e
        }
    }
    
    private fun displayNote(note: WorkoutNote) {
        Log.d(TAG, "displayNote: Displaying note: ${note.title}")
        binding.tvTitle.text = note.title
        // Display exercises with steps and key points
        // This is a simplified version - you would create a proper UI for this
        val exercisesText = note.exercises.joinToString("\n\n") { exercise ->
            "${exercise.name}\n" +
            "步骤:\n${exercise.steps.joinToString("\n") { "• $it" }}\n" +
            "要点:\n${exercise.keyPoints.joinToString("\n") { "• $it" }}"
        }
        binding.tvContent.text = exercisesText
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

