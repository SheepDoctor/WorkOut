package com.example.workout.ui.notes

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.workout.data.model.WorkoutNote
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class NoteDetailViewModel : ViewModel() {
    private val _note = MutableStateFlow<WorkoutNote?>(null)
    val note: StateFlow<WorkoutNote?> = _note.asStateFlow()
    
    fun loadNote(noteId: String) {
        viewModelScope.launch {
            // In real implementation, load from database
            // For now, return mock data
            _note.value = WorkoutNote(
                id = noteId,
                title = "健身笔记",
                exercises = emptyList(),
                createdAt = System.currentTimeMillis()
            )
        }
    }
}

