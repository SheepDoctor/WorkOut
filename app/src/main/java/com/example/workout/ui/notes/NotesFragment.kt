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
import androidx.recyclerview.widget.LinearLayoutManager
import com.example.workout.R
import com.example.workout.databinding.FragmentNotesBinding
import kotlinx.coroutines.launch

class NotesFragment : Fragment() {
    companion object {
        private const val TAG = "NotesFragment"
    }
    private var _binding: FragmentNotesBinding? = null
    private val binding get() = _binding!!
    
    private val viewModel: NotesViewModel by viewModels()
    private lateinit var notesAdapter: NotesAdapter
    
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
            _binding = FragmentNotesBinding.inflate(inflater, container, false)
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
            notesAdapter = NotesAdapter { note ->
                Log.d(TAG, "onViewCreated: Note clicked: ${note.id}")
                try {
                    val bundle = Bundle().apply {
                        putString("noteId", note.id)
                    }
                    findNavController().navigate(R.id.action_notes_to_note_detail, bundle)
                } catch (e: Exception) {
                    Log.e(TAG, "onViewCreated: Error navigating to note detail", e)
                }
            }
            
            binding.recyclerView.apply {
                layoutManager = LinearLayoutManager(requireContext())
                adapter = notesAdapter
            }
            
            viewLifecycleOwner.lifecycleScope.launch {
                try {
                    viewModel.notes.collect { notes ->
                        Log.d(TAG, "onViewCreated: Notes updated, count: ${notes.size}")
                        if (notes.isEmpty()) {
                            binding.tvEmpty.visibility = View.VISIBLE
                            binding.recyclerView.visibility = View.GONE
                        } else {
                            binding.tvEmpty.visibility = View.GONE
                            binding.recyclerView.visibility = View.VISIBLE
                            notesAdapter.submitList(notes)
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "onViewCreated: Error observing notes", e)
                }
            }
            
            viewModel.loadNotes()
            Log.d(TAG, "onViewCreated: Completed successfully")
        } catch (e: Exception) {
            Log.e(TAG, "onViewCreated: Error setting up views", e)
            throw e
        }
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

