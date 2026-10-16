/**
 * Marlin 3D Printer Firmware
 * Copyright (c) 2020 MarlinFirmware [https://github.com/MarlinFirmware/Marlin]
 *
 * Based on Sprinter and grbl.
 * Copyright (c) 2011 Camiel Gubbels / Erik van der Zalm
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 *
 */

//
// SD Card Menu
//

#include "../../inc/MarlinConfigPre.h"

#if ALL(HAS_MARLINUI_MENU, HAS_MEDIA)

#include "menu_item.h"
#include "../../sd/cardreader.h"

void lcd_sd_updir() {
  ui.encoderPosition = card.cdup() ? ENCODER_STEPS_PER_MENU_ITEM : 0;
  encoderTopLine = 0;
  ui.screen_changed = true;
  ui.refresh();
}

// Neva : nom (8.3) du dernier fichier lance depuis l'ecran, pour proposer de le reimprimer a la fin
static char neva_last_file[16];     // nom court 8.3 (sert a relancer l'impression)
static char neva_last_name[32];     // nom long (sert a l'affichage)

// Neva : goto_screen() remet la selection de l'ecran de confirmation sur "Annuler" ; on la force sur "Imprimer" au premier
// affichage de l'ecran (ce drapeau est leve juste avant goto_screen puis consomme par l'ecran)
static bool neva_confirm_first = false;

#if ENABLED(SD_REPRINT_LAST_SELECTED_FILE)

  uint16_t sd_encoder_position = 0xFFFF;
  int8_t sd_top_line, sd_items;

  // Neva : a la fin d'une impression, ecran "Reimprimer <fichier> ?" avec "Imprimer" deja selectionne : un clic relance
  void MarlinUI::reselect_last_file() {
    if (!neva_last_file[0]) return;
    defer_status_screen();
    neva_confirm_first = true;
    goto_screen([]{
      if (neva_confirm_first) { neva_confirm_first = false; ui.set_selection(true); }
      MenuItem_confirm::select_screen(
        GET_TEXT_F(MSG_BUTTON_PRINT), GET_TEXT_F(MSG_BUTTON_CANCEL),
        []{ card.openAndPrintFile(neva_last_file); ui.return_to_status(); ui.reset_status(); }, nullptr,
        F("Reimprimer"), neva_last_name, F(" ?")
      );
    });
    TERN_(HAS_TOUCH_SLEEP, ui.wakeup_screen());
  }

#endif

inline void sdcard_start_selected_file() {
  strncpy(neva_last_file, card.filename, sizeof(neva_last_file) - 1);
  strncpy(neva_last_name, card.longest_filename(), sizeof(neva_last_name) - 1);
  card.openAndPrintFile(card.filename);
  ui.return_to_status();
  ui.reset_status();
}

// Neva : entree "Imprimer le dernier" du menu principal. La liste est triee du plus recent au plus ancien : le premier
// fichier (pas un dossier) de la racine est le dernier copie sur la carte. Ecran de confirmation, "Imprimer" selectionne.
void neva_print_latest_file() {
  card.mount();               // remonte la carte et revient a la racine
  ui.reinit_lcd();
  const int16_t n = card.get_num_items();
  for (int16_t i = 0; i < n; i++) {
    card.selectFileByIndexSorted(i);
    if (card.flag.filenameIsDir) continue;
    strncpy(neva_last_file, card.filename, sizeof(neva_last_file) - 1);
    strncpy(neva_last_name, card.longest_filename(), sizeof(neva_last_name) - 1);
    neva_confirm_first = true;
    ui.goto_screen([]{
      if (neva_confirm_first) { neva_confirm_first = false; ui.set_selection(true); }
      MenuItem_confirm::select_screen(
        GET_TEXT_F(MSG_BUTTON_PRINT), GET_TEXT_F(MSG_BUTTON_CANCEL),
        []{ card.openAndPrintFile(neva_last_file); ui.return_to_status(); ui.reset_status(); }, nullptr,
        F("Imprimer le dernier"), neva_last_name, F(" ?")
      );
    });
    return;
  }
  ui.set_status(F("Aucun fichier"));
}

class MenuItem_sdfile : public MenuItem_sdbase {
  public:
    static inline void draw(const bool sel, const uint8_t row, FSTR_P const fstr, CardReader &theCard) {
      MenuItem_sdbase::draw(sel, row, fstr, theCard, false);
    }
    static void action(FSTR_P const fstr, CardReader &) {
      #if ENABLED(SD_REPRINT_LAST_SELECTED_FILE)
        // Save menu state for the selected file
        sd_encoder_position = ui.encoderPosition;
        sd_top_line = encoderTopLine;
        sd_items = screen_items;
      #endif
      #if ENABLED(SD_MENU_CONFIRM_START)
        neva_confirm_first = true;   // Neva : "Imprimer" est selectionne d'office (un seul clic de plus pour lancer)
        MenuItem_submenu::action(fstr, []{
          if (neva_confirm_first) { neva_confirm_first = false; ui.set_selection(true); }
          char * const filename = card.longest_filename();
          MenuItem_confirm::select_screen(
            GET_TEXT_F(MSG_BUTTON_PRINT), GET_TEXT_F(MSG_BUTTON_CANCEL),
            sdcard_start_selected_file, nullptr,
            GET_TEXT_F(MSG_START_PRINT), filename, F("?")
          );
        });
      #else
        sdcard_start_selected_file();
        UNUSED(fstr);
      #endif
    }
};

class MenuItem_sdfolder : public MenuItem_sdbase {
  public:
    static inline void draw(const bool sel, const uint8_t row, FSTR_P const fstr, CardReader &theCard) {
      MenuItem_sdbase::draw(sel, row, fstr, theCard, true);
    }
    static void action(FSTR_P const, CardReader &theCard) {
      card.cd(theCard.filename);
      encoderTopLine = 0;
      ui.encoderPosition = 2 * (ENCODER_STEPS_PER_MENU_ITEM);
      ui.screen_changed = true;
      TERN_(HAS_MARLINUI_U8GLIB, ui.drawing_screen = false);
      ui.refresh();
    }
};

void menu_media_filelist() {
  ui.encoder_direction_menus();

  #if HAS_MARLINUI_U8GLIB
    static int16_t fileCnt;
    if (ui.first_page) fileCnt = card.get_num_items();
  #else
    const int16_t fileCnt = card.get_num_items();
  #endif

  START_MENU();
  #if ENABLED(MULTI_VOLUME)
    ACTION_ITEM(MSG_BACK, []{ ui.goto_screen(menu_media); });
  #else
    BACK_ITEM_F(TERN1(BROWSE_MEDIA_ON_INSERT, screen_history_depth) ? GET_TEXT_F(MSG_MAIN_MENU) : GET_TEXT_F(MSG_BACK));
  #endif
  if (card.flag.workDirIsRoot) {
    #if !HAS_SD_DETECT
      ACTION_ITEM(MSG_REFRESH, []{ encoderTopLine = 0; card.mount(); });
    #endif
  }
  else if (card.isMounted())
    ACTION_ITEM_F(F(LCD_STR_FOLDER " .."), lcd_sd_updir);

  if (ui.should_draw()) {
    for (int16_t i = 0; i < fileCnt; i++) {
      if (_menuLineNr != _thisItemNr)
        SKIP_ITEM();
      else {
        card.selectFileByIndexSorted(i);
        if (card.flag.filenameIsDir)
          MENU_ITEM(sdfolder, MSG_MEDIA_MENU, card);
        else
          MENU_ITEM(sdfile, MSG_MEDIA_MENU, card);
      }
    }
  }
  END_MENU();
}

#if ENABLED(MULTI_VOLUME)
  void menu_media_select() {
    START_MENU();
    BACK_ITEM_F(TERN1(BROWSE_MEDIA_ON_INSERT, screen_history_depth) ? GET_TEXT_F(MSG_MAIN_MENU) : GET_TEXT_F(MSG_BACK));
    #if ENABLED(VOLUME_SD_ONBOARD)
      ACTION_ITEM(MSG_SD_CARD, []{ card.changeMedia(&card.media_driver_sdcard); card.mount(); ui.goto_screen(menu_media_filelist); });
    #endif
    #if ENABLED(VOLUME_USB_FLASH_DRIVE)
      ACTION_ITEM(MSG_USB_DISK, []{ card.changeMedia(&card.media_driver_usbFlash); card.mount(); ui.goto_screen(menu_media_filelist); });
    #endif
    END_MENU();
  }
#endif

void menu_media() {
  TERN(MULTI_VOLUME, menu_media_select, menu_media_filelist)();
}

#endif // HAS_MARLINUI_MENU && HAS_MEDIA
