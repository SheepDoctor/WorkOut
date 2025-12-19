package com.example.workout.ui.notes

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import com.example.workout.data.model.WorkoutNote
import com.example.workout.databinding.FragmentNoteDetailBinding
import kotlinx.coroutines.launch

class NoteDetailFragment : Fragment() {
    private var _binding: FragmentNoteDetailBinding? = null
    private val binding get() = _binding!!
    
    private val args: NoteDetailFragmentArgs by navArgs()
    private val viewModel: NoteDetailViewModel by viewModels()
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentNoteDetailBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        binding.toolbar.setNavigationOnClickListener {
            findNavController().navigateUp()
        }
        
        viewLifecycleOwner.lifecycleScope.launch {
            viewModel.note.collect { note ->
                note?.let {
                    displayNote(it)
                }
            }
        }
        
        viewModel.loadNote(args.noteId)
    }
    
    private fun displayNote(note: WorkoutNote) {
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
        _binding = null
    }
}

