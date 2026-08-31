class CreatePharmacies < ActiveRecord::Migration[8.1]
  def change
    create_table :pharmacies do |t|
      t.string :name
      t.string :base_domain
      t.string :logo_url
      t.boolean :active

      t.timestamps
    end
  end
end
