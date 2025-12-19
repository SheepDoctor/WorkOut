package com.example.workout.ui.notes

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.workout.data.model.WorkoutNote
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class NotesViewModel : ViewModel() {
    private val _notes = MutableStateFlow<List<WorkoutNote>>(emptyList())
    val notes: StateFlow<List<WorkoutNote>> = _notes.asStateFlow()
    
    fun loadNotes() {
        viewModelScope.launch {
            // In real implementation, load from database
            // For now, return empty list or mock data
            _notes.value = emptyList()
        }
    }
    
    fun deleteNote(noteId: String) {
        viewModelScope.launch {
            _notes.value = _notes.value.filter { it.id != noteId }
            // In real implementation, delete from database
        }
    }
}

