package com.example.workout.ui.notes

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.example.workout.data.model.WorkoutNote
import com.example.workout.databinding.ItemNoteBinding
import java.text.SimpleDateFormat
import java.util.*

class NotesAdapter(
    private val onNoteClick: (WorkoutNote) -> Unit
) : ListAdapter<WorkoutNote, NotesAdapter.NoteViewHolder>(NoteDiffCallback()) {
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): NoteViewHolder {
        val binding = ItemNoteBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return NoteViewHolder(binding, onNoteClick)
    }
    
    override fun onBindViewHolder(holder: NoteViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
    
    class NoteViewHolder(
        private val binding: ItemNoteBinding,
        private val onNoteClick: (WorkoutNote) -> Unit
    ) : RecyclerView.ViewHolder(binding.root) {
        
        fun bind(note: WorkoutNote) {
            binding.tvTitle.text = note.title
            binding.tvExerciseCount.text = "${note.exercises.size} 个动作"
            
            val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())
            binding.tvDate.text = dateFormat.format(Date(note.createdAt))
            
            binding.root.setOnClickListener {
                onNoteClick(note)
            }
        }
    }
    
    class NoteDiffCallback : DiffUtil.ItemCallback<WorkoutNote>() {
        override fun areItemsTheSame(oldItem: WorkoutNote, newItem: WorkoutNote): Boolean {
            return oldItem.id == newItem.id
        }
        
        override fun areContentsTheSame(oldItem: WorkoutNote, newItem: WorkoutNote): Boolean {
            return oldItem == newItem
        }
    }
}

