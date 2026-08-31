class CreateMedicines < ActiveRecord::Migration[8.1]
  def change
    create_table :medicines do |t|
      t.string :name
      t.string :active_ingredient
      t.string :dosage
      t.boolean :bioequivalent

      t.timestamps
    end
  end
end
